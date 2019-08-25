import login_to_db
import time

class export_fx_usd_jpy(login_to_db.login_to_db):

	def export(self, bid_output, ask_output):
		#self.func = func
		self.bid_output = bid_output
		self.ask_output = ask_output

		quant_trading_database = super().login_to_quant_trading()

		#Creating insert command into database. 
		sql_insert_querry = """ INSERT INTO fx_usd_jpy (date_time, bid, ask) VALUES (%s, %s, %s)"""
		insert_data = (time.time(), self.bid_output, self.ask_output)

		#Create cursor.
		cursor = quant_trading_database.cursor()

		#Execute querry
		cursor.execute(sql_insert_querry, insert_data)
		quant_trading_database.commit()

		#return self.func(*args, **kwargs)