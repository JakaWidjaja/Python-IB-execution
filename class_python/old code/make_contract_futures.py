import sys
sys.path.insert(0, '/media/lun/Data2/Trading_Algo/IbPy-master/ib/ext')

from IBWrapper import contract
import make_contract

'''
This class is to create a contract for Forex.
Use to make transaction or creating market data. 
'''

class make_contract_futures(make_contract.make_contract):
	def __init__(self, symbol, sec_type, exchange, currency, right, strike, expiry, 
					   multiplier, trading_class):

		self._symbol = symbol
		self._sec_type = sec_type
		self._exchange = exchange
		self._currency = currency
		self._right = right
		self._strike = strike
		self._expiry = expiry
		self._multiplier = multiplier
		self._trading_class = trading_class

	
	def make_contract(self):
		#Initialised contract object from IB library. 
		create = contract()

		#Create contract info. 
		contract_info = create.create_contract(symbol = self._symbol, 
											   secType = self._sec_type,
											   exchange = self._exchange,
											   currency = self._currency,
											   right = self._right,
											   strike = self._strike, 
											   expiry = self._expiry, 
											   multiplier = self._multiplier,
											   tradingClass = self._trading_class)

		return contract_info