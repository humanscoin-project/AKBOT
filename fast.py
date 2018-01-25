#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2, json, thread, sys
from decimal import getcontext,Decimal
from sys import exc_clear
import wexlib
import time
getcontext().prec = 8
number_digits = 6
# config
#############################################################################
key = 'XXXXXXXX-XXXXXXXX-XXXXXXXX-XXXXXXXX-XXXXXXXX'                        # API key
secret = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX' # API secret
Funds1 = 'ltc'
Funds2 = 'usd'
minimum_funds1 = 0.25
minimum_funds2 = 15
#############################################################################
pair = Funds1 + '_' + Funds2 
api = wexlib.PublicAPIv3()
tapi = wexlib.TradeAPIv1({'Key': key, 'Secret': secret})

def funds1():
    return tapi.call('getInfo')['funds'][Funds1]

def funds2():
    return tapi.call('getInfo')['funds'][Funds2]

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

def price_buy_profit():
	print " Buying Fixed " , (price_sell() + Decimal(0.000001)) , Funds2.upper()
	return (price_sell() + Decimal(0.000001))

def price_sell_profit():
    if price_sell() < (price_buy() - (price_buy() * Decimal(0.004))):
        print " Selling Fixed " , (price_buy() - Decimal(0.000001)) , Funds2.upper()
        return (price_buy() - Decimal(0.000001))
    else:
        print " Selling " , sell_profit() , Funds2.upper()
        return sell_profit()

def buy():
    return tapi.call( 'Trade', type = 'buy', pair = pair, rate = price_buy_profit(), amount = 0.23456789 )

def sell():
    return tapi.call( 'Trade', type='sell', pair = pair, rate = price_sell_profit(), amount = 0.23456789 )

def brule():		"""\ """
    if funds2() > minimum_funds2 and price_buy() > (price_sell() + (price_sell() * Decimal(0.004))):
        return True
    else:
        return False

def srule():		"""\ """
    if funds1() > minimum_funds1 and price_sell() < (price_buy() - (price_buy() * Decimal(0.004))) and price_buy() > last_buy_price() + ( last_buy_price() * Decimal(0.004)):
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
	if price_buy_profit() != price_sell():
		cancel_order()
		cancel_order()
		if brule() == True:
			buy()
	if price_sell_profit() != price_buy():
		cancel_order()
		cancel_order()
		if srule() == True:
			sell()
	time.sleep(10)