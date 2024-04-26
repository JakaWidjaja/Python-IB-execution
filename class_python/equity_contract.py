import make_contract

class equity_contract(make_contract.make_contract):
	def __init__(self, contract_object):
		#Contract object from IBWrapper
		self.contract_object = contract_object
		self.create = self.contract_object()

	def stock_aud(self, stock_symbol):
		self.stock_symbol = stock_symbol

		#Create contract info
		contract_info = self.create.create_contract(self.stock_symbol, 
													'STK', 
													'SMART',
													'AUD')

		return contract_info

	def stock_usd(self, stock_symbol):
		self.stock_symbol = stock_symbol
		
		#Create contract info
		contract_info = self.create.create_contract(self.stock_symbol, 
													'STK', 
													'SMART',
													'USD')

		return contract_info

	def stock_gbp(self, stock_symbol):
		self.stock_symbol = stock_symbol

		#Create contract info
		contract_info = self.create.create_contract(self.stock_symbol, 
													'STK', 
													'SMART',
													'GBP')

		return contract_info