import sys
sys.path.insert(0, '/media/lun/Data2/Trading_Algo/IbPy-master/ib/ext')

from IBWrapper import contract
import make_contract

'''
This class is to create a contract for Forex.
Use to make transaction or creating market data. 
'''

class make_contract_forex(make_contract.make_contract):
	def make_contract(self, underlying, sec_type, exchange, currency):
		#Initialised arguments.
		self._underlying = underlying
		self._sec_type = sec_type
		self._exchange = exchange
		self._currency = currency

		#Initialised contract object from IB library. 
		create = contract()

		#Create contract info. 
		contract_info = create.create_contract(symbol = self._underlying, 
											   secType = self._sec_type,
											   exchange = self._exchange,
											   currency = self._currency)

		return contract_info

