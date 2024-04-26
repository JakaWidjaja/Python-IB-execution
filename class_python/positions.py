import numpy as np

class positions():
	def __init__(self):
		pass

	def stock_position(self, weight, cash, bid_ask):
		'''
		Calculate the position taken
		'''
		self.weight  = weight
		self.cash    = cash
		self.bid_ask = bid_ask #array, index 0 for bid

		if weight < 0.0:
			pos = np.floor(weight * cash / bid_ask[0])
		elif weight == 0:
			pos = 0
		else:
			pos = np.floor(weight * cash / bid_ask[1]) 

		return pos


