import make_contract

class spx_contract(make_contract.make_contract):
	def __init__(self, contract_object):
		#Contract object from IBWrapper
		self.contract_object = contract_object
		self.create = self.contract_object()

	def futures(self, month_expiry, year_expiry):
		#Initiate arguments.
		self.month_expiry = month_expiry
		self.year_expiry = year_expiry

		#===================================================
		#***************************************************
		#Create the expiry.
		#Convert the month with leading zero.
		if (self.month_expiry <= 9):
			 self.month_expiry = "%02d" % (self.month_expiry)

		#convert the year to expiry to string. 
		self.year_expiry = str(self.year_expiry)

		#Create the expiry. 
		expiry = self.year_expiry + self.month_expiry
		#***************************************************
		#===================================================

		#Create contract info.
		#If the expiry is provided, then the VIX code name is not required. 
		contract_info = self.create.create_contract(symbol = 'SPX', 
											   		secType = 'FUT',
											   		exchange = 'GLOBEX',
											   		currency = 'USD',
											   		right = None,
											   		strike = None, 
											   		expiry = expiry, 
											   		multiplier = None,
											   		tradingClass = 'SP')

		return contract_info


	def option(self, opt_type, opt_strike, month_expiry, year_expiry):
		'''
		Argument:
			opt_type: This is a string either a 'Call' or 'Put'
			opt_strike: the option strike
			month_expiry: an integer for the expiry month
			year_expiry: an integer for the expiry year 
		'''

		#Initiate variables.
		self.opt_type = opt_type
		self.opt_strike = opt_strike
		self.month_expiry = month_expiry
		self.year_expiry = year_expiry

		#===================================================
		#***************************************************
		#Create the expiry.
		#Convert the month with leading zero.
		if (self.month_expiry <= 9):
			 self.month_expiry = "%02d" % (self.month_expiry)

		#convert the year to expiry to string. 
		self.year_expiry = str(self.year_expiry)

		#Create the expiry. 
		expiry = self.year_expiry + str(self.month_expiry)
		#***************************************************
		#===================================================

		#Create the data for VIX option. 
		#If the expiry is provided, then the SPX code name is not required. 
		contract_info = self.create.create_contract(symbol = 'SPX',
											   		secType = 'OPT', 
											   		exchange = 'SMART',
											   		currency = 'USD', 
											   		right = self.opt_type,
											   		strike = str(self.opt_strike),
											   		expiry = expiry,
											   		multiplier = 100, 
											   		tradingClass = 'SPX')

		return contract_info