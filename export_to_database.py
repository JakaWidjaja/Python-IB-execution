import login_to_db
import time

class export_to_database(login_to_db.login_to_db):

	def export_fx(self, bid_output, ask_output, expiry_date, strike, database_table):
		#self.func = func
		self.bid_output = bid_output
		self.ask_output = ask_output
		self.database_table = database_table
		self.expiry_date = expiry_date
		self.strike = strike

		quant_trading_database = super().login_to_quant_trading()

		#Table name.
		table_name = self.database_table

		#Creating insert command into database. 
		sql_insert_querry = " INSERT INTO " +  table_name + \
							"(date_time, bid, ask, strike, expiry) VALUES (%s, %s, %s, %s, %s)"
		insert_data = (time.time(), self.bid_output, self.ask_output, self.strike, self.expiry_date)

		#Create cursor.
		cursor = quant_trading_database.cursor()

		#Execute querry
		cursor.execute(sql_insert_querry, insert_data)
		quant_trading_database.commit()