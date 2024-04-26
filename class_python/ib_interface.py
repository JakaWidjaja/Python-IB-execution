import sys
sys.path.insert(0, '/media/lun/Data2/Trading_Algo/IbPy-master/ib/ext')

import pandas as pd
import time

#import the tws library
from IBWrapper import IBWrapper, contract
from EClientSocket import EClientSocket

import time

#Use facade method

#This class containt the neccessary connection to IB interface. 

#Initiate IB functions. 
call_back = IBWrapper()
tws = EClientSocket(call_back)


class ib_interface:	

	def __init__(self, host, port, client_id):
		self.host      = host
		self.port      = port
		self.client_id = client_id
		
		#Connect to trade workstation. 
		tws.eConnect(self.host, self.port, self.client_id)

		#Initiate variables from IB class.
		call_back.initiate_variables()
	
	
	def create_data(self, contract_details, ticker_id, timer):
		'''
		This method is used to create market data. 
		argument:
			contract_details: details of contracts, for example, futures, forex, etc
			ticker_id: 		  unique identifier. can be any random number (integer).
			timer:			  A delay time. Needed to establish connection with TWS. 

		Output:
			An array containing the bid and ask. Bid first then ask second. 
		'''

		#Initiate argument. 
		self.contract_details = contract_details
		self.ticker_id        = ticker_id	
		self.timer            = timer

		tws.reqMarketDataType(4) #Delayed market data.
		
		#Request market data. 
		#If set to true then only snapshot. 
		tws.reqMktData(self.ticker_id, self.contract_details, '', True) 

		#Need to wait a while for the IB to response, so put a wait timer. 
		time.sleep(self.timer)

    	#Get the bid and ask price/data. 
		bid = call_back.tick_Price[-2][2]
		ask = call_back.tick_Price[-1][2]

		#Create the output as a list. 
		output = [bid, ask]

		return output

	def calculate_implied_vol(self, order_id, contract_info, option_price, spot_price):
		'''
		This method uses Interactive Broker's calculator to calculate the implied
		volatility of an option
		arguments:
			order_id: just a random integer to identify the order number
			contract_info: the details of the options
			option_price: the option's premium
			spot_price: the underlying price
		'''

		#Initiate argument.
		self.order_id      = order_id
		self.contract_info = contract_info
		self.option_price  = option_price
		self.spot_price    = spot_price

		imp_vol = tws.calculateImpliedVolatility(self.order_id,
												self.contract_info,
												self.option_price,
												self.spot_price)

		return imp_vol

	def make_transaction(self, account_name, order_id, contract_info, amount, order_type):
		'''
		This method allows a buy or sell transaction. 
		arguments:
			order_id:
			contract_info: the contract information for the instrument
			order_info:
		'''
		self.account_name  = account_name
		self.order_id      = order_id
		self.contract_info = contract_info
		self.amount        = amount
		self.order_type    = order_type

		create = contract()	

		if self.amount == 0:
			return None
		elif self.amount < 0:
			amount *= -1
			order_info = create.create_order(self.account_name, self.order_type, self.amount, 'SELL')
		elif self.amount > 0:
			order_info = create.create_order(self.account_name, self.order_type, self.amount, 'BUY')
		
		tws.placeOrder(self.order_id, self.contract_info, order_info)
		'''
		#Check the amount of filled order
		while True: 
			order_stat = pd.DataFrame(call_back.order_Status, columns = ['order ID', 'status', 'filled', 
    													'remaining', 'ave fill price', 'perm id', 
    													'parent id', 'last fill price', 'client id', 
    													'why held'])
			timer_start = time.time()

	    	if not order_stat.empty:
		        return order_stat.loc[order_stat['status'] == 'Filled', 'filled'].values
		        break

		    time_end = time.time()

		    if (time_end - time_start) == 2: #2 seconds limit
		    	print("order not placed")
		    	break
		'''

	def account_cash_info(self, account_name, currency):
		'''
		This method allows user to obtain the amount of cash available in the account
		arguments:
			account_name:
			currency    : the cash currency
		'''
		self.account_name = account_name
		self.currency     = currency

		tws.reqAccountUpdates(True, self.account_name)
		tws.reqAccountSummary(True, "account_name", 'NetLiquidation')
		tws.reqPositions()

		time.sleep(0.1)

		account_value = pd.DataFrame(call_back.update_AccountValue, 
							 columns = ['key', 'value', 'currency', 'accountName'])

		cash_amount = account_value.loc[(account_value['key'] == 'TotalCashBalance') & 
						  				(account_value['currency'] == self.currency), 'value'].iat[0]

		return cash_amount

	def account_position_info(self, account_name):
		'''
		This method obtain the actual position 
		'''


