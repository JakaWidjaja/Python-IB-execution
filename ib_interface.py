import sys
sys.path.insert(0, '/media/lun/Data2/Trading_Algo/IbPy-master/ib/ext')

#import the tws library
from IBWrapper import IBWrapper
from EClientSocket import EClientSocket

import time

#Use facade method

#This class containt the neccessary connection to IB interface. 

#Initiate IB functions. 
call_back = IBWrapper()
tws = EClientSocket(call_back)


class ib_interface:	

	def __init__(self, host, port, client_id):
		self.host = host
		self.port = port
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
		self.ticker_id = ticker_id	
		self.timer = timer

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

	def make_transaction(self, order_id, contract_info, order_info):
		'''
		This method allows a buy or sell transaction. 
		arguments:
			order_id:
			contract_info: the contract information for the instrument
			order_info:
		'''
		pass


