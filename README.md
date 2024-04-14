# Easee EV Charger Price Updater
Updates Easee EV Charger with currenct charging cost, I made this to work in Norway, but it shouldn't be much work to make it work for other countries.
I used the hvakosterstrommen.no API to get the spot price, then add the fees and other costs that I know the local power company charges, add vat and formats it into NOK.

At the moment the scripts gets the price in Norwegian Øre, then transfer fees are added before VAT are added to the total, then the additional fees are added. It's then converted to a whole Norwegian Krone before its uploaded using the Easee API.

**Features:**
 - [X] Goverment rebate calculations (Strømstøtte).
 - [X] Auto refreshes tokens.


### Information you need to set this up Easee:

 - Easee Site ID:
   - You can find this information when logged in to Easee cloud services.
   - https://easee.cloud/sites
 - Access Token:
   - Using their developer page and API endpoints.
   - https://developer.easee.com/docs/authentication-1
 - Refresh Token:
   - Same as above, requires an additional post function using username and pass to send get a response from their API.
   - https://developer.easee.com/reference/post_api-accounts-refresh-token
  
 - Power transfer fee, night and day.
 - Additional costs.
