import sys
sys.path.insert(0, '/media/lun/Data2/Trading_Algo/IbPy-master/ib/ext')
sys.path.insert(0, '/media/lun/Data2/Trading_Algo/class')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
from datetime import datetime

import mysql.connector as mysql
from ib_interface import ib_interface
import market_data
import vix_contract
import make_contract

from IBWrapper import IBWrapper, contract
from EClientSocket import EClientSocket
from ScannerSubscription import ScannerSubscription

import output_data

if __name__ == '__main__':
	
	#==========================================================================
	#**************************************************************************
	#Login to interactive brokers. 
	account_name = 'DU229425'
	port = 7497
	client_id = 5000
	host = ''

	#Initiate object. 
	#This part also automatically perform a login into TWS. 
	connection_ib = ib_interface(host, port, client_id)
	#**************************************************************************
	#==========================================================================
	

	#==========================================================================
	#**************************************************************************
	#VIX contract data.
	#These are the details from IB. Need this to get the data.  
	vix_symbol = 'VXZ9'
	vix_sec_type = 'FUT'
	vix_exchange = 'CFE'
	vix_currency = 'USD'
	vix_right = None
	vix_strike = None
	vix_expiry = '201912'
	vix_multiplier = None
	vix_trading_class = None

	stock_underlying = 'AUD'
	stock_sec_type = 'CASH'
	stock_exchange = 'IDEALPRO'
	stock_currency = 'USD'

	#Create a unique ticker ID.
	ticker_id = 1002


	cont = vix_contract.vix_contract()#.vix_futures(8, 2019)
	#cont1 = cont.futures('Call', 15, 8, 2019)
	cont1 = cont.futures(8, 2019)


	call_back = IBWrapper() 	#Instantiate IBWrapper, callback

	tws = EClientSocket(call_back)	#Instantiate EClientSocket and return data to callback
	tws.reqMarketDataType(3) #Delayed market data. 

	count = 1

	while True:
		#Get the data.
		#initialise object. 

		market = market_data.market_data(connection_ib, cont1)
		#data = output_data.output_data(connection_ib, cont1)
		getting_data = market.get_data(ticker_id, 1, 'vix_option')
		#getting_data = data.output_forex(ticker_id, 2, 'fx_usd_jpy')
		#getting_data = connection_ib.create_data(futures_contract, ticker_id, 1.5)

		#data = getting_data.create_data()
		print('bid:',getting_data[0])
		print('ask:',getting_data[1])

		count += 1
		if count == 10:
			break
	#**************************************************************************
	#==========================================================================









