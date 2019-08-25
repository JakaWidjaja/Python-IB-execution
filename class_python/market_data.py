import sys
sys.path.insert(0, '/media/lun/Data2/Trading_Algo/class')

import export_to_database

class market_data():
	def __init__(self, ib_create_data, contract_info):
		'''
		Argument:
			ib_create_data: This is the connection to IB interface. 
			contract_info: The contract information to feed into the IB interface. 
		'''
		self.ib_create_data = ib_create_data
		self.contract_info = contract_info

	def get_data(self, ticker_id, sleep_time, table_name):
		#initialised arguments.
		self.ticker_id = ticker_id	#Unique ticker ID.
		self.sleep_time = sleep_time	#Time delay. 
		self.table_name = table_name #database table name

		#Create bid and ask data
		bid_ask_data = self.ib_create_data.create_data(self.contract_info, self.ticker_id, self.sleep_time)

		#Export these data into a database. 
		export = export_to_database.export_to_database()
		export.export_fx(bid_ask_data[0], bid_ask_data[1], self.contract_info.m_expiry, \
						 self.contract_info.m_strike, self.table_name)

		return bid_ask_data