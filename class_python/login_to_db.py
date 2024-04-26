import mysql.connector as mysql

class login_to_db():
	def login_to_quant_trading(self):

		host = 'localhost'
		user = 'root'
		password = 'prawira8'
		database_name = 'quant_trading' 

		#Login to database. 
		database =  mysql.connect(host = host, user = user, passwd = password, db = database_name)

		return database
