#import export_to_database
import queue

class output_data():
	def __init__(self, ib_create_data, contract_info):
		'''
		Argument:
			ib_create_data: This is the connection to IB interface. 
			contract_info: The contract information to feed into the IB interface. 
		'''
		self.ib_create_data = ib_create_data
		self.contract_info = contract_info


	#==================================================================================
	#**********************************************************************************
	def output_forex(self, ticker_id, sleep_time, table_name):
		#initialised arguments.
		self.ticker_id = ticker_id	#Unique ticker ID.
		self.sleep_time = sleep_time	#Time delay. 
		self.table_name = table_name #database table name

		#Create bid and ask data
		#Vector. First item is the bid and second is ask number. 
		try:
			bid_ask_data = self.ib_create_data.create_data(self.contract_info, self.ticker_id, self.sleep_time)
		except:
			bid_ask_data = [0,0]

		#==========================================================
		#==========================================================
		#Export these data into a database. 
		export = export_to_database.export_to_database()
		export.export_fx(bid_ask_data[0], bid_ask_data[1], self.table_name)
		#==========================================================
		#==========================================================

		return bid_ask_data
	#**********************************************************************************
	#==================================================================================

	#==================================================================================
	#**********************************************************************************
	def output_futures_spx(self, month_expiry, year_expiry, ticker_id, sleep_time, table_name):
		#Initialised arguments.
		self.month_expiry = month_expiry
		self.year_expiry = year_expiry
		self.ticker_id = ticker_id 		#unique ticker ID.
		self.sleep_time = sleep_time	#Time delay.
		self.table_name = table_name	#database table name. 

		#Create bid and ask data
		#Vector. First item is the bid and second is ask number. 
		try:
			bid_ask_data = self.ib_create_data.create_data(self.contract_info, self.ticker_id, self.sleep_time)
		except:
			bid_ask_data = [0,0]

		#==========================================================
		#==========================================================
		#Export these data into a database. 
		export = export_to_database.export_to_database()
		export.export_futures(bid_ask_data[0], bid_ask_data[1], self.month_expiry, self.year_expiry, self.table_name)
		#==========================================================
		#==========================================================

		return bid_ask_data
	#**********************************************************************************
	#==================================================================================

	#==================================================================================
	#**********************************************************************************
	def output_option_spx(self, strike, month_expiry, year_expiry, 
						  ticker_id, sleep_time, table_name):
		#Initialised arguments
		self.strike = strike
		self.month_expiry = month_expiry
		self.year_expiry = year_expiry
		self.ticker_id = ticker_id
		self.sleep_time = sleep_time
		self.table_name = table_name

		#Create bid and ask data
		#Vector. First item is the bid and second is ask number. 
		try:
			bid_ask_data = self.ib_create_data.create_data(self.contract_info, self.ticker_id, self.sleep_time)
		except:
			bid_ask_data = [0,0]

		imp_vol_bid = 0.0
		imp_vol_ask = 0.0

		#==========================================================
		#==========================================================
		#Export these data into a database. 
		export = export_to_database.export_to_database()
		export.export_option(bid_ask_data[0], bid_ask_data[1], 
							 self.strike,
							 imp_vol_bid, imp_vol_ask,
							 self.month_expiry,
							 self.year_expiry,
							 self.table_name)
		#==========================================================
		#==========================================================

		return bid_ask_data
	#**********************************************************************************
	#==================================================================================

	#==================================================================================
	#**********************************************************************************
	def output_batch_option_spx(self):
		
		pass
	#**********************************************************************************
	#==================================================================================

	#==================================================================================
	#**********************************************************************************
	def output_futures_vix(self, month_expiry, year_expiry, ticker_id, sleep_time, table_name):
		#Initialised arguments.
		self.month_expiry = month_expiry
		self.year_expiry = year_expiry
		self.ticker_id = ticker_id 		#unique ticker ID.
		self.sleep_time = sleep_time	#Time delay.
		self.table_name = table_name	#database table name. 

		#Create bid and ask data
		#Vector. First item is the bid and second is ask number. 
		try:
			bid_ask_data = self.ib_create_data.create_data(self.contract_info, self.ticker_id, self.sleep_time)
		except:
			bid_ask_data = [0,0]

		#==========================================================
		#==========================================================
		#Export these data into a database. 
		export = export_to_database.export_to_database()
		export.export_futures(bid_ask_data[0], bid_ask_data[1], self.month_expiry, self.year_expiry, self.table_name)
		#==========================================================
		#==========================================================

		return bid_ask_data
	#**********************************************************************************
	#==================================================================================

	#==================================================================================
	#**********************************************************************************
	def output_option_vix(self, strike, month_expiry, year_expiry, 
						  ticker_id, sleep_time, table_name):

		#Initialised arguments
		self.strike = strike
		self.month_expiry = month_expiry
		self.year_expiry = year_expiry
		self.ticker_id = ticker_id
		self.sleep_time = sleep_time
		self.table_name = table_name

		#Create bid and ask data
		#Vector. First item is the bid and second is ask number. 
		try:
			bid_ask_data = self.ib_create_data.create_data(self.contract_info, self.ticker_id, self.sleep_time)
		except:
			bid_ask_data = [0,0]

		#Calculate the implied volatility
		#Calculate the bid implied volatility
		try:
			
			imp_vol_bid = ib_interface.calculate_implied_vol(self.ticker_id, 
															 self.contract_info, 
															 bid_ask_data[0],
															 self.spot_bid)
			
			#imp_vol_bid = 8.8
		except:
			imp_vol_bid = 0.00
		#calculate the ask implied volatility
		try:
			
			imp_vol_ask = ib_interface.calculate_implied_vol(self.ticker_id,
															 self.contract_info,
															 bid_ask_date[1],
															 self.spot_ask)
			
			#imp_vol_ask = 8.8
		except:
			imp_vol_ask = 0.00

		imp_vol_bid = 8.8
		imp_vol_ask = 8.8

		#==========================================================
		#==========================================================
		#Export these data into a database. 
		export = export_to_database.export_to_database()
		export.export_option(bid_ask_data[0], bid_ask_data[1], 
							 self.strike,
							 imp_vol_bid, imp_vol_ask,
							 self.month_expiry,
							 self.year_expiry,
							 self.table_name)
		#==========================================================
		#==========================================================

		return bid_ask_data
	#**********************************************************************************
	#==================================================================================

	#==================================================================================
	#**********************************************************************************
	def output_equity(self, stock_name, currency, ticker_id, sleep_time, table_name):
		#initialised arguments
		self.stock_name = stock_name
		self.currency = currency
		self.ticker_id = ticker_id
		self.sleep_time = sleep_time
		self.table_name = table_name

		#Create bid and ask data
		#Vector. First item is the bid and second is ask number. 
		try:
			bid_ask_data = self.ib_create_data.create_data(self.contract_info, self.ticker_id, self.sleep_time)
		except:
			bid_ask_data = [0,0]

		#==========================================================
		#==========================================================
		'''
		#Create table name
		table_name = "equity_" + self.currency + "_" + self.stock_name

		#export these data into a database. 
		export = export_to_database.export_to_database()
		export.export_equity(self.stock_name, bid_ask_data[0], bid_ask_data[1], self.table_name)
		'''
		#==========================================================
		#==========================================================

		return bid_ask_data
	#**********************************************************************************
	#==================================================================================