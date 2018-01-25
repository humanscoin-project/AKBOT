#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2, json, thread, sys
from decimal import getcontext,Decimal
from sys import exc_clear
import wexlib
import time
rest = 0
getcontext().prec = 6
number_digits = 3 # After point how much number 0.X = 1 | 0.XX = 2 | 0.XXX = 3 | 0.XXXX = 4
# config
#############################################################################
key = 'XXXXXXXX-XXXXXXXX-XXXXXXXX-XXXXXXXX-XXXXXXXX'                        # API key
secret = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX' # API secret
Funds1 = 'btc' # пари Вставте тут бажану першу валюту торгівлі. (Дрібні букви)
Funds2 = 'usd' # Insert here the desired trading second currency.
minimum_funds1 = 0.001 # Insert here the minimum_funds1 allowed in each transaction.
minimum_funds2 = 6 # Insert here the minimum_funds2 allowed in each transaction.
amount_buy_percent =  0 #0.1 = 10% | 0.5 = 50% | or you can use 0 for 100%
amount_sell_percent =  0 #
#############################################################################
pair = Funds1 + '_' + Funds2 
api = wexlib.PublicAPIv3()
tapi = wexlib.TradeAPIv1({'Key': key, 'Secret': secret})

print "Wellcome in AKBOT fast"
def funds1():
    return tapi.call('getInfo')['funds'][Funds1]

def funds2():
    return tapi.call('getInfo')['funds'][Funds2]

def price_buy():
    return api.call('ticker')[pair]['buy']

def price_sell():
    return api.call('ticker')[pair]['sell']

def average_price():
    return price_sell() + ((price_buy()-price_sell()) / 2)

def all_balance():
    return funds2() + (funds1() * average_price())

print " You Have :" ,all_balance() , Funds2.upper()
def last_trade_hist(): ## Get last 100 trades for history analysis.
    return dict.values(tapi.call('TradeHistory', pair = pair, count = 100))

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
    return round(last_sell_price() - (last_sell_price() * Decimal(0.004)), number_digits) # Decimal(скільки прибутку) = 0.002 0.2% / 0.005 0.5% / 0.01 1%

def fix_price_buy_profit():
    if price_sell() < price_buy_profit() and price_buy() > (price_sell() + (price_sell() * Decimal(0.003))):
        print " Buying Fixed " , (price_sell() + Decimal(0.01)) , Funds2.upper()
        return (price_sell() + Decimal(0.01))
    if price_sell() > price_buy_profit():
        print " Buying " , price_buy_profit() , Funds2.upper()
        return price_buy_profit()

def price_sell_profit():
    return round(last_buy_price() + ( last_buy_price() * Decimal(0.004)), number_digits) # Decimal(скільки прибутку) = 0.002 0.2% / 0.005 0.5% / 0.01 1%

def fix_price_sell_profit():
    if price_buy() > price_sell_profit() and price_sell() < (price_buy() - (price_sell() * Decimal(0.003))):
        print " Selling Fixed " , (price_buy() - Decimal(0.01)) , Funds2.upper()
        return (price_buy() - Decimal(0.01))
    if price_buy() < price_sell_profit():
        print " Selling " , price_sell_profit() , Funds2.upper()
        return price_sell_profit()


def buy():
    return tapi.call( 'Trade', type = 'buy', pair = pair, rate = fix_price_buy_profit(), amount = amount_to_buy())

def sell():
    return tapi.call( 'Trade', type='sell', pair = pair, rate = fix_price_sell_profit(), amount = amount_to_sell())

def brule1():
    if funds2() > minimum_funds2:
        return True
    else:
        return False

def srule1():
    if funds1() > minimum_funds1:
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
	try:
		if rest < 1:
			cancel_order()
			cancel_order()
			rest = 2
			print " You Have :" ,all_balance() , Funds2.upper()
			if price_buy() < (last_buy_price() - (last_buy_price() * Decimal(0.01))) and funds1() > minimum_funds1:
				print " Stop Loss"
				tapi.call( 'Trade', type='sell', pair = pair, rate = (price_buy() - Decimal(0.01)), amount = amount_to_sell())
				time.sleep(10)
				cancel_order()
				time.sleep(3)
				if price_buy() < (last_buy_price() - (last_buy_price() * Decimal(0.01))) and funds1() > minimum_funds1:
					print " Stop Loss"
					tapi.call( 'Trade', type='sell', pair = pair, rate = (price_buy() - Decimal(0.01)), amount = amount_to_sell())
					time.sleep(10)
					cancel_order()
					time.sleep(3)
					if price_buy() < (last_buy_price() - (last_buy_price() * Decimal(0.01))) and funds1() > minimum_funds1:
						print " Stop Loss"
						tapi.call( 'Trade', type='sell', pair = pair, rate = (price_buy() - Decimal(0.01)), amount = amount_to_sell())
						time.sleep(10)
		if brule1() == True:
			buy()
			rest = 2
		if srule1() == True:
			sell()
			rest = 2
		time.sleep(20)
		rest = rest - 1
	except Exception:
		time.sleep(10)
		print " ########################################### "
		print " ##     Sorry. something went wrong       ## "
		print " ########################################### "