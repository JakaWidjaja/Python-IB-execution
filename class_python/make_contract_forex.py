import make_contract

'''
This class is to create a contract for Forex.
Use to make transaction or creating market data. 
'''

class make_contract_forex(make_contract.make_contract):
	def __init__(self, contract_object):
		self.contract_object = contract_object
		self.create = self.contract_object()

	def forex(self, underlying, sec_type, exchange, currency):
		#Initialised arguments.
		self._underlying = underlying
		self._sec_type = sec_type
		self._exchange = exchange
		self._currency = currency

		#Create contract info. 
		contract_info = self.create.create_contract(symbol = self._underlying, 
											   		secType = self._sec_type,
											   		exchange = self._exchange,
											   		currency = self._currency)

		return contract_info

