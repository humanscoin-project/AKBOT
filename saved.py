#!/usr/bin/env python
# -*- coding: utf-8 -*-
import wexlib
import time
import os
import sys
import collections
import threading
from decimal import Decimal
# config
#############################################################################
key = 'XXXXXXXX-XXXXXXXX-XXXXXXXX-XXXXXXXX-XXXXXXXX'                        # API key
secret = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX' # API secret
#############################################################################
asset = 'ppc'		    # asset or coin | btc , ltc , eth , dsh
currency = 'usd'	    # currency | usd , rur , eur or btc
amount_buy_percent= 0	#0.1 = 10% | 0.5 = 50% | or you can use 0 for 100%
amount_sell_percent= 0	# amount to sell percent 0.1 = 10% | 0.5 = 50% | or you can use 0 for 100%
Fee=0.2			        # Sensor sensitivity to prices
minimum_asset = 0.1 	# minimum asset you can trading
minimum_currency = 5	# minimum currency you can trading
max_digits_amount = 3 	# max digits after point 0.XXX = 3 0.XXXXXX = 6
max_digits_price = 3 	# max digits after point 0.XXX = 3 0.XXXXXX = 6
#########################

pair = asset.lower() + '_' + currency.lower()
api = wexlib.PublicAPIv3()
tapi = wexlib.TradeAPIv1({'Key': key, 'Secret': secret})
fee=Fee/100
ping_price = float(str(0.) + str(0) * (max_digits_price - 2) + str(1))
ping_amount = float(str(0.) + str(0) * (max_digits_amount - 2) + str(1))
asset_btc = asset.lower() + '_btc'
btc_currency = 'btc_' + currency.lower()

os.system(['clear','cls'][os.name == 'nt'])
print " ------------------------------------------- "
print " ******** Wellcome in WEX AKBOT ************"
print " ------------------------------------------- "
print "\t        " ,asset.upper(), "<->", currency.upper()
print "\t       Fee    :" , 100*fee , "%"

def asset_balance():
	return tapi.call('getInfo')['funds'][asset]

def currency_balance():
	return tapi.call('getInfo')['funds'][currency]

def price_buy():
	return api.call('ticker')[pair]['buy']

def price_sell():
	return api.call('ticker')[pair]['sell'] 

def price_asset_btc():
	return api.call('ticker')[asset_btc]['sell']

def price_btc_currency():
	return api.call('ticker')[btc_currency]['sell']

saved_buy = price_buy()
saved_sell = price_sell()

def center_price():
	return price_sell() + ((price_buy()-price_sell()) / 2)

def amount_to_buy():
	if amount_buy_percent != 0:
		return round(Decimal(amount_buy_percent) * currency_balance() / price_buy(),max_digits_amount)
	else:
		return round((currency_balance() / price_buy())  -  Decimal(ping_amount),max_digits_amount)

def amount_to_sell():
	if amount_sell_percent != 0:
		return round(Decimal(amount_sell_percent) * asset_balance(),max_digits_amount)
	else:
		return round(asset_balance() -  Decimal(ping_amount),max_digits_amount)

def price_buy_profit_max():
	return round(price_sell() + Decimal(ping_price), max_digits_price)

def price_buy_profit_mini():
	return round(price_sell() + ((center_price() - price_sell()) / 2), max_digits_price)

def price_sell_profit_max():
	return round(price_buy() - Decimal(ping_price), max_digits_price)

def price_sell_profit_mini():
	return round(price_buy() - ((price_buy() - center_price()) / 2), max_digits_price)

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

def cancel_order():
	try:
		active = tapi.call('ActiveOrders', pair = pair)
		return tapi.call('CancelOrder', order_id = active.items()[0][0])
	except:
		pass

def buy():
	print " ########################################### "
	print " ##   Waiting Buy orders to complete.     ## "
	print " ########################################### "
	print " [" + str(price_buy_profit_max() * float(amount_to_buy())) + " " + str(currency.upper()) + " >>>>>>>>>>> " + str(amount_to_buy()) + " " + str(asset.upper()) + "]"
	tapi.call( 'Trade', type = 'buy', pair = pair, rate = price_buy_profit_max(), amount = amount_to_buy())
	time.sleep(20)
	cancel_order()
	time.sleep(3)
	if amount_to_buy() > minimum_asset:
		print " [" + str(price_buy_profit_mini() * float(amount_to_buy())) + " " + str(currency.upper()) + " >>>>>>>>>>> " + str(amount_to_buy()) + " " + str(asset.upper()) + "]"
		tapi.call( 'Trade', type='buy', pair = pair, rate = price_buy_profit_mini(), amount = amount_to_buy())
		time.sleep(10)
		cancel_order()

def sell():
	print " ########################################### "
	print " ##   Waiting Sell Orders To Complete.    ## "
	print " ########################################### "
	print " [" + str(amount_to_sell()) + " " + str(asset.upper()) + " >>>>>>>>>>> " + str(price_sell_profit_max() * float(amount_to_sell())) + " " + str(currency.upper()) + "]"
	tapi.call( 'Trade', type='sell', pair = pair, rate = price_sell_profit_max(), amount = amount_to_sell())
	time.sleep(30)
	cancel_order()
	time.sleep(3)
	if amount_to_sell() > minimum_asset:
		print " [" + str(amount_to_sell()) + " " + str(asset.upper()) + " >>>>>>>>>>> " + str(price_sell_profit_mini() * float(amount_to_sell())) + " " + str(currency.upper()) + "]"
		tapi.call( 'Trade', type='sell', pair = pair, rate = price_sell_profit_mini(), amount = amount_to_sell())
		time.sleep(20)
		cancel_order()
		time.sleep(3)
		if amount_to_sell() > minimum_asset:
			stop_loss()

def stop_loss():
	if price_buy() < last_buy_price():
		print " [" + str(amount_to_sell()) + " " + str(asset.upper()) + " >>>>>>>>>>> " + str(price_sell() * float(amount_to_sell())) + " " + str(currency.upper()) + "]"
		force_sell()
	else:
		print " ########################################### "
		print " ##    Not lost over fee. cancel order    ## "
		print " ########################################### "

def force_sell():
	return tapi.call( 'Trade', type='sell', pair = pair, rate = price_sell(), amount = amount_to_sell())

def balance():
	print " ------------------------------------------- "
	print " "*12 + (time.strftime("%d.%m.%Y - %H:%M:%S"))
	print " ------------------------------------------- "
	print " \tBalance Asset    : " , round(asset_balance(),3) , " " + asset.upper()
	print " \tBalance currency : " , round(currency_balance(),3) , " " + currency.upper()
	print " ------------------------------------------- "
balance()
def cond_buy():		"""\ center > saved buy + fee /\ price asset btc * price btc currency > saved buy"""
	if center_price() > saved_buy + ((saved_buy * Decimal(fee))*2) and price_asset_btc() * price_btc_currency() > saved_buy():
		return True
	else:
		return False

def cond_sell():	"""\ center < saved sell - fee /\ last buy price + price btc currency < saved_sell"""
	if center_price() < saved_sell - ((saved_sell * Decimal(fee))*2) and price_asset_btc() + price_btc_currency() < saved_sell():
		return True
	else:
		return False

while True:
	try:
		profit = round(( price_sell() - last_buy_price() - ((price_sell() * Decimal(fee))*2))/last_buy_price() * 100,1)
		#----------------------------------
		if saved_buy > price_buy(): # min
			saved_buy = price_buy()
		if saved_sell < price_sell(): # max
			saved_sell = price_sell()
		#----------------------------------
		if cond_buy() == True:
			print " ------------------ Rise ------------------- "
			saved_buy = price_buy()
			if amount_to_buy() > minimum_currency:
				buy()
				balance()
		if cond_sell() == True:
			print " ----------------- Decline ----------------- "
			saved_sell = price_sell()
			if amount_to_sell() > minimum_asset:
				sell()
				balance()
		#----------------------------------
		if asset_balance() > minimum_asset and currency_balance() < minimum_currency:
			status = "\tCenter :" + str(round(center_price(),2)) +"\tProfit:" + str(profit) + "%"
		elif asset_balance() < minimum_asset and currency_balance() > minimum_currency:
			status = "\tCenter:" + str(round(center_price(),2)) + "\tLast:" + str(round( price_buy() - last_sell_price(),3)) + " "+ str(currency.upper())
		else:
			status = "\tBuy:" + str(round(price_buy(),2)) + "\tSell:" + str(round(price_sell(),2))
		time.sleep(10)
		print " [",round(price_asset_btc() * price_btc_currency(),2),"]" , status
	except Exception:
		time.sleep(10)
		print " ########################################### "
		print " ##     Sorry. something went wrong       ## "
		print " ########################################### "
