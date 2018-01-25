#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2, json, thread, sys
from decimal import getcontext,Decimal
from sys import exc_clear
import wexlib
import time
getcontext().prec = 8
number_digits = 7
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
pair = Funds1 + '_' + Funds2 
api = wexlib.PublicAPIv3()
tapi = wexlib.TradeAPIv1({'Key': key, 'Secret': secret})
def funds1():
    return tapi.call('getInfo')['funds'][Funds1]

def funds2():
    return tapi.call('getInfo')['funds'][Funds2]

def amount_to_buy():
    if amount_buy_percent != 0:
        return Decimal(amount_buy_percent) * funds2() / price_buy()
    else:
        return funds2() / price_buy()
    

def amount_to_sell():
    if amount_sell_percent != 0:
        return Decimal(amount_sell_percent) * funds1()
    else:
        return funds1()

def price_buy():
    return api.call('ticker')[pair]['buy']

def price_sell():
    return api.call('ticker')[pair]['sell']

def last_trade_hist():
    return dict.values(tapi.call('TradeHistory', pair = pair, count = 100))

def last_buy_price():
    lst = ([ i for i in last_trade_hist() if i['type'] == 'buy' ])
    timestamp = max( ([ el[u'timestamp'] for el in lst ]) )
    for ele in lst:
        if ele['timestamp'] == timestamp:
            return ele[u'rate']
            
def last_sell_price():
    lst = ([ i for i in last_trade_hist() if i['type'] == 'sell' ])
    timestamp = max( ([ el['timestamp'] for el in lst ]) )
    for ele in lst:
        if ele['timestamp'] == timestamp:
            return ele['rate']

def buy_profit():
    return round(last_sell_price() - (last_sell_price() * Decimal(0.005)), number_digits)

def price_buy_profit():
    if price_sell() < (price_buy() - (price_buy() * Decimal(0.005))):
        print " Buying Fixed " , (price_sell() + Decimal(0.001)) , Funds2.upper()
        return (price_sell() + Decimal(0.001))
    else:
        print " Buying " , buy_profit() , Funds2.upper()
        return buy_profit()

def sell_profit():
    return round(last_buy_price() + ( last_buy_price() * Decimal(0.005)), number_digits)

def price_sell_profit():
    if price_buy() > (price_sell() + (price_sell() * Decimal(0.005))):
        print " Selling Fixed " , (price_buy() - Decimal(0.001)) , Funds2.upper()
        return (price_buy() - Decimal(0.001))
    else:
        print " Selling " , sell_profit() , Funds2.upper()
        return sell_profit()

def buy():
    return tapi.call( 'Trade', type = 'buy', pair = pair, rate = price_buy_profit(), amount = amount_to_buy() )

def sell():
    return tapi.call( 'Trade', type='sell', pair = pair, rate = price_sell_profit(), amount = amount_to_sell() )

def brule():		"""\ """
    if funds2() > minimum_funds2 and price_sell() < (price_buy() - (price_buy() * Decimal(0.005))):
        return True
    else:
        return False

def srule():		"""\ """
    if funds1() > minimum_funds1 and price_buy() > (price_sell() + (price_sell() * Decimal(0.005))):
        return True
    else:
        return False

def cancel_order():
    try:
        active = tapi.call('ActiveOrders', pair = pair)
        return tapi.call('CancelOrder', order_id = active.items()[0][0])
    except:
        pass

while True:
	cancel_order()
	cancel_order()
	if brule() == True:
		buy()
	if srule() == True:
		sell()
	time.sleep(10)
