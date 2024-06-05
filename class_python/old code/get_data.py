import sys
sys.path.insert(0, '/media/lun/Data2/Trading_Algo/IbPy-master/ib/ext')
import time
import pandas as pd

#libaries from IB.
from EClientSocket import EClientSocket
from IBWrapper import IBWrapper, contract

#Import abstract class.
import make_data
'''
account_name = "DU229343"
port = 7497 #4002 7497
client_ID = 5000
host = ''

call_back = IBWrapper() 	#Instantiate IBWrapper, callback
tws = EClientSocket(call_back)	#Instantiate EClientSocket and return data to callback
tws.eConnect(host, port, client_ID) #Connect to tws
call_back.initiate_variables()
'''
class get_data(make_data.make_data):
	def __init__(self, conn, contract_details, ticker_id):
		'''
		contract_details is the class to get the contract(i.e. stocks, futures, options, etc)
		ticker_id is a unique identifier. Just need to be any unique number.
		'''
		self.contract_details = contract_details
		self.ticker_id = ticker_id
		self.conn = conn


	def create_data(self):
		call_back = IBWrapper()

		#Request market data. 
		#If set to true then only snapshot. 
		self.conn.reqMktData(self.ticker_id, self.contract_details, '', True) 

		#Need to wait a while for the IB to response, so put a wait timer. 
		time.sleep(0.5)

		#Create tick data.
		tick_data = pd.DataFrame(self.conn.tick_Price, columns = ['tickerId', 'field', 'price', 
    															  'canAutoExecute'])

    	#Get the bid and ask price/data. 
		bid = call_back.tick_Price[-2][2]
		ask = call_back.tick_Price[-1][2]

		#Create the output as a list. 
		output =[bid, ask]

		return output