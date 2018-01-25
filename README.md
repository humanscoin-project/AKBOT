## AKBOT (WEX.NZ)
# config
#############################################################################

key = 'XXXXXXXX-XXXXXXXX-XXXXXXXX-XXXXXXXX-XXXXXXXX'                        # API key

secret = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX' # API secret

Funds1 = 'btc'

Funds2 = 'usd'

minimum_funds1 = 0.001

minimum_funds2 = 7

amount_buy_percent =  0 #0.1 = 10% | 0.5 = 50% | or you can use 0 for 100%

amount_sell_percent =  0 #

#############################################################################

#Install

sudo npm install -g forever

forever start <path to your server javascript>
