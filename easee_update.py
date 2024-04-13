from datetime import datetime
import pytz
import requests
import json

""" This script is created for use in Norway with Easee EV chargers.
    It will download the current spot price, add the transmission fees,
    misc costs and vat.
    
    
    It will then update the charger using the API, and refresh the token
    to keep updating the chargers automatically. This script should be set
    to scheduled running every hour."""

timezone = pytz.timezone("Europe/Oslo")
now = datetime.now(tz=timezone)
year = now.year
month = now.month
hour = now.hour
day = now.day

SITE_ID = 'https://easee.cloud/sites'
URL_AUTHENTICATION = 'https://developer.easee.com/docs/authentication-1'
URL_REFRESH_TOKEN = ('https://developer.easee.com/reference/post_api-accounts'
                     '-refresh-token')

try:
    with open("data.json", mode="r") as settings_file:
        settings = json.load(settings_file)
except FileNotFoundError:
    settings = {}
    print(f'\nSite ID can be found at: {SITE_ID}')
    settings["site_id"] = int(input("Site ID: "))
    print(f'\nYour local power distribute has this information.')
    settings["transmission_day"] = float(input("Transmission fee daytime: "))
    settings["transmission_night"] = float(
        input("Transmission fee nighttime: "))
    print("Misc other fees.")
    settings["misc_costs"] = float(input("Additional costs: ")) / 100
    print(f"\nType what power zone you're in: NO1, NO2, NO3, NO4, NO5 or NO6.")
    settings["zone"] = str(input("Zone: "))
    print(f"\nAccess Token can be setup here: {URL_AUTHENTICATION}")
    settings["access_token"] = str(input("Access Token: "))
    print(f"\nRefresh Token can be found here: {URL_REFRESH_TOKEN}")
    settings["refresh_token"] = str(input("Refresh Token: "))
    with open("data.json", mode="w") as settings_file:
        json.dump(settings, settings_file, indent=4)

# Transmission fee:
if 6 < hour < 22:
    transfer_fee = settings["transmission_day"] / 100
else:
    transfer_fee = settings["transmission_night"] / 100

# Format date:
if len(str(month)) < 2:
    month = f"0{month}"

if len(str(day)) < 2:
    day = f"0{day}"


def get_price():
    price_url = (f'https://www.hvakosterstrommen.no/api/v1/prices/{year}/'
                 f'{month}-{day}_{settings["zone"].upper()}.json')
    response = requests.get(url=price_url)
    price = response.json()
    kwh_price = price[hour]["NOK_per_kWh"]
    kwh_price_total = round(
        (kwh_price + settings["misc_costs"] / 100) * 1.25 + transfer_fee, 2)
    print(f'Calculated kwh in NOK: {kwh_price_total}.')
    return kwh_price_total


def refresh_token():
    bearer_token = f'Bearer: {settings["access_token"]}'
    url = 'https://api.easee.com/api/accounts/refresh_token'
    payload = ("{\"accessToken\":\"" + settings["access_token"] +
               "\",\"refreshToken\":\"" + settings["refresh_token"] + "\"}")
    headers = {'accept': "application/json",
               'content-type': "application/*+json",
               'Authorization': bearer_token}

    response = requests.post(url, data=payload, headers=headers)
    new_data = response.json()
    new_access_token = new_data["accessToken"]
    new_refresh_token = new_data["refreshToken"]

    settings["refresh_token"] = new_refresh_token
    settings["access_token"] = new_access_token

    with open('data.json', mode='w') as update_file:
        json.dump(settings, update_file, indent=4)
    return response


def update_price():
    new_kwh_price = get_price()
    url_easee = f'https://api.easee.com/api/sites/{settings["site_id"]}/price'
    payload = f"{{\"currencyId\":\"NOK\",\"costPerKWh\":{new_kwh_price}" + "}"
    headers = {"content-type": "application/*+json",
               'Authorization': 'Bearer ' + settings["access_token"]}
    response = requests.post(url_easee, data=payload, headers=headers)
    return response


try:
    new_price = update_price()
    if new_price.status_code == 200:
        print('Price was updated successfully.')
    else:
        print('Price update failed.')
except requests.exceptions.HTTPError:
    new_token = refresh_token()
    if new_token.status_code == 200:
        print('Tokes was refreshed.')
        retry = update_price()
        if retry.status_code == 200:
            print('Price was updated successfully.')
        else:
            retry.raise_for_status()
            print('Unable to update price.')
    else:
        new_token.raise_for_status()
        print('Unable to update refresh token.')