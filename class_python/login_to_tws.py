import sys
sys.path.insert(0, '/media/lun/Data2/Trading_Algo/IbPy-master/ib/ext')

#import the tws library
from IBWrapper import IBWrapper
from EClientSocket import EClientSocket

import time
import pandas as pd

#Set the number of time to try to log-in. 
number_of_try = 1

account_name = 'DU228378'
port = 7497
client_id = 5000
host = ''

class login_to_tws:
	call_back = IBWrapper()
	call_back.initiate_variables()
	tws = EClientSocket(call_back)
	tws.eConnect(host, port, client_id)

	def login(self,  host, port, client_id):
		#Initialised arguments
		self.host = host
		self.port = port
		self.client_id = client_id


	def create_data(self,contract_details, ticker_id):
		self.contract_details = contract_details
		self.ticker_id = ticker_id

		#Request market data. 
		#If set to true then only snapshot. 
		self.tws.reqMktData(self.ticker_id, self.contract_details, '', True) 

		#Need to wait a while for the IB to response, so put a wait timer. 
		time.sleep(2)

		#Create tick data.
		tick_data = pd.DataFrame(self.call_back.tick_Price, columns = ['tickerId', 'field', 'price', 
    															  'canAutoExecute'])

    	#Get the bid and ask price/data. 
		bid = self.call_back.tick_Price[-2][2]
		ask = self.call_back.tick_Price[-1][2]

		#Create the output as a list. 
		output =[bid, ask]

		return output
