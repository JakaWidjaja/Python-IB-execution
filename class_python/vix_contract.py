import sys
sys.path.insert(0, '/media/lun/Data2/Trading_Algo/IbPy-master/ib/ext')

from IBWrapper import contract
import make_contract

class vix_contract(make_contract.make_contract):

	def futures(self, month_expiry, year_expiry):
		#Initiate arguments.
		self.month_expiry = month_expiry
		self.year_expiry = year_expiry

		#Create contract object
		create = contract()

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
		contract_info = create.create_contract(symbol = 'VIX', 
											   secType = 'FUT',
											   exchange = 'CFE',
											   currency = 'USD',
											   right = None,
											   strike = None, 
											   expiry = expiry, 
											   multiplier = None,
											   tradingClass = 'VX')

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

		#Create contract object
		create = contract()

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

		#Create the data for VIX option. 
		#If the expiry is provided, then the VIX code name is not required. 
		symbol = 'VIX'
		sec_type = 'OPT'
		exchange = 'SMART'
		currency = 'USD'
		right = self.opt_type
		strike = self.opt_strike

		contract_info = create.create_contract(symbol = 'VIX',
											   secType = 'OPT', 
											   exchange = 'SMART',
											   currency = 'USD', 
											   right = self.opt_type,
											   strike = str(self.opt_strike),
											   expiry = expiry,
											   multiplier = 100, 
											   tradingClass = 'VIX')

		return contract_info