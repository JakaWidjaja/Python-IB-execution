import sys
sys.path.insert(0, '/home/lun/Desktop/Folder 2/Trading_Algo/IbPy-master/ib/ext')
sys.path.insert(0, '/home/lun/Desktop/Folder 2/Trading_Algo/ibapi')
sys.path.insert(0, '/home/lun/Desktop/Folder 2/Trading_Algo/class_python')
sys.path.insert(0, '/home/lun/Desktop/Folder 2/Python/model/mean portfolio')
sys.path.insert(0, '/home/lun/Desktop/Folder 2/Python/model/ornstein uhlenbeck')

import numpy as np
import pandas as pd
import time
from datetime import datetime
from collections import deque
from positions import positions

#import mysql.connector as mysql
from ib_interface import ib_interface
import equity_contract
import output_data

from client import EClient
from wrapper import EWrapper
from IBWrapper import IBWrapper, contract
from EClientSocket import EClientSocket
from ScannerSubscription import ScannerSubscription

from portfolio import portfolio
from ornstein_uhlenbeck import oh_model

#==========================================================================
#**************************************************************************
#Initialised library function
np_array = np.array
np_sum = np.sum
np_transpose = np.transpose
np_average = np.average
#**************************************************************************
#==========================================================================

#==========================================================================
#**************************************************************************
#Initialised portfolio
lag = 1
mean_portfolio = portfolio()

#Initialised weights
weights = np_array([0.5, 0.5, 0.5])

#length of list
max_length = 100

#Amount of cash available
long_portfolio_cash  = 3000.0
short_portfolio_cash = 3000.0
#**************************************************************************
#==========================================================================

#==========================================================================
#**************************************************************************
#Market open 10 am. 

time_open = datetime.strptime("05:00:00", "%H:%M:%S") #Delay start time
#time_close = datetime.strptime("16:20:00", "%H:%M:%S") #Delay close time
#**************************************************************************
#==========================================================================
	
#==========================================================================
#**************************************************************************
#Login to interactive brokers. 
account_name = 'DU012'
port = 7497
client_id = 5001
host = ''

#Initiate object. 
#This part also automatically perform a login into TWS. 
connection_ib = ib_interface(host, port, client_id)
#**************************************************************************
#==========================================================================

#==========================================================================
#**************************************************************************
#Initialise variables for model.
enter_short_trigger = False
enter_long_trigger = False

enter_short_position = False
enter_long_position = False

long_xom_position = 0
long_cvx_position = 0
long_bp_position = 0

short_xom_position = 0
short_cvx_position = 0
short_bp_position = 0

long_stop_loss  = 0.0
short_stop_loss = 0.0

pos = positions()

order_type = 'MKT'

#Create a unique ticker ID.
long_xom_count = 1000
long_cvx_count = long_xom_count + 1
long_bp_count = long_cvx_count + 1

short_xom_count = long_bp_count + 1
short_cvx_count = short_xom_count + 1
short_bp_count = short_cvx_count + 1

eq = equity_contract.equity_contract(contract)
xom_cont = eq.stock_gbp('XOM')
cvx_cont = eq.stock_aud('CVX')
bp_cont = eq.stock_aud('BP')

time_delay = 2.0

xom_mid_price = 0.0
cvx_mid_price = 0.0
bp_mid_price = 0.0

xom_bid = deque(maxlen = int(max_length))
xom_ask = deque(maxlen = int(max_length))
cvx_bid = deque(maxlen = int(max_length))
cvx_ask = deque(maxlen = int(max_length))
bp_bid = deque(maxlen = int(max_length))
bp_ask = deque(maxlen = int(max_length))

xom_mid = deque()
cvx_mid = deque()
bp_mid = deque()

while (time_open.time() <= datetime.now().time()): #and time_close.time() >= datetime.now().time()):
	#Create connection
	xom_data = output_data.output_data(connection_ib, xom_cont)
	cvx_data = output_data.output_data(connection_ib, cvx_cont)
	bp_data  = output_data.output_data(connection_ib, bp_cont)

	#Get bid ask data
	xom_bid_ask = xom_data.output_equity('XOM', 'USD', long_xom_count, time_delay, 'equity')
	cvx_bid_ask = cvx_data.output_equity('CVX', 'USD', long_cvx_count, time_delay, 'equity')
	bp_bid_ask  = bp_data.output_equity('BP', 'USD', long_bp_count, time_delay, 'equity')

	#Increment count
	long_xom_count = long_bp_count + 1
	long_cvx_count = long_xom_count + 1
	long_bp_count = long_cvx_count + 1

	#Calculate mid price
	xom_mid_price = np_average(xom_bid_ask)
	cvx_mid_price = np_average(cvx_bid_ask)
	bp_mid_price = np_average(bp_bid_ask)

	#Store the mid price
	xom_mid.append(xom_mid_price)
	cvx_mid.append(cvx_mid_price)
	bp_mid.append(bp_mid_price)
	time_series = np_array([xom_mid, cvx_mid, bp_mid])


	if(len(xom_mid) < max_length):
		xom_bid.append(xom_bid_ask[0])
		xom_ask.append(xom_bid_ask[1])
		cvx_bid.append(cvx_bid_ask[0])
		cvx_ask.append(cvx_bid_ask[1])
		bp_bid.append(bp_bid_ask[0])
		bp_ask.append(bp_bid_ask[1])

	else:
		#Update list
		xom_bid.popleft()
		xom_ask.popleft()
		cvx_bid.popleft()
		cvx_ask.popleft()
		bp_bid.popleft()
		bp_ask.popleft()

		xom_bid.append(xom_bid_ask[0])
		xom_ask.append(xom_bid_ask[1])
		cvx_bid.append(cvx_bid_ask[0])
		cvx_ask.append(cvx_bid_ask[1])
		bp_bid.append(bp_bid_ask[0])
		bp_ask.append(bp_bid_ask[1])

		#Calculate portfolio weights
		weights = mean_portfolio.box_tiao(time_series,lag, weights)

		#Get the amount of cash available
		cash = connection_ib.account_cash_info(account_name, 'USD')

		if (not enter_long_position) and (not enter_short_position):
			long_portfolio_cash  = cash / 2.0
			short_portfolio_cash = cash / 2.0
		elif (not enter_long_position) and enter_short_position:
			long_portfolio_cash  = cash
			short_portfolio_cash = 0.0
		elif enter_long_position and (not enter_short_position):
			long_portfolio_cash  = 0.0
			short_portfolio_cash = cash

		#Calculate the number of stocks for each assets
		if not enter_long_portfolio:
			long_xom_position = int(weights[0] * long_portfolio_cash / xom_mid_price)
			long_cvx_position = int(weights[1] * long_portfolio_cash / cvx_mid_price)
			long_bp_position = int(weights[2] * long_portfolio_cash / bp_mid_price)

		if not enter_short_portfolio:
			short_xom_position = int(weights[0] * short_portfolio_cash / xom_mid_price) * -1
			short_cvx_position = int(weights[1] * short_portfolio_cash / cvx_mid_price) * -1
			short_bp_position = int(weights[2] * short_portfolio_cash / bp_mid_price) * -1

		#Calculate portfolio tick value
		#Long Portfolio
		if long_xom_position >= 0:
			long_xom_price = long_xom_position * np_array(xom_ask)
		else:
			long_xom_price = long_xom_position * np_array(xom_bid)

		if long_cvx_position >= 0:
			long_cvx_price = long_cvx_position * np_array(cvx_ask)
		else:
			long_cvx_price = long_cvx_position * np_array(cvx_bid)

		if long_bp_position >= 0:
			long_bp_price = long_bp_position * np_array(bp_ask)
		else:
			long_bp_price = long_bp_position * np_array(bp_bid)

		#Short position 
		if short_xom_position >= 0:
			short_xom_price = short_xom_position * np_array(xom_ask)
		else:
			short_xom_price = short_xom_position * np_array(xom_bid)

		if short_cvx_position >= 0:
			short_cvx_price = short_cvx_position * np_array(cvx_ask)
		else:
			short_cvx_price = short_cvx_position * np_array(cvx_bid)

		if short_bp_position >= 0:
			short_bp_price = short_bp_position * np_array(bp_ask)
		else:
			short_bp_price = short_bp_position * np_array(bp_bid)

		long_price  = long_xom_price  + long_cvx_price  + long_bp_price
		short_price = short_xom_price + short_cvx_price + short_bp_price

		#Calculate the upper and lower bound
		#Normalised the data first then calibrate OH model 
		#Normalised the data
		long_min = min(long_price)
		long_max = max(long_price)
		short_min = min(short_price)
		short_max = max(short_price)

		long_normalised = (long_price - long_min) / (long_max - long_min)
		short_normalised = (short_price - short_min) / (short_max - short_min)

		#Calculate the OH Parameters
		long_mean_revert_port = oh_model(long_price)
		short_mean_revert_port = oh_model(short_price)

		long_mu, long_theta, long_sigma = long_mean_revert_port.method_of_moment()
		short_mu, short_theta, short_sigma = short_mean_revert_port.method_of_moment()

		#Calculate the top and bottom boundary
		long_above_normalised = long_theta + long_sigma / long_mu
		long_below_normalised = long_theta - long_sigma / long_mu
		short_above_normalised = short_theta + short_sigma / short_mu
		short_below_normalised = short_theta - short_sigma / short_mu

		#Unnormalised
		long_average = long_theta * (long_max - long_min) + long_min
		short_average = short_theta * (short_max - short_min) + short_min

		long_above = long_above_normalised * (long_max - long_min) + long_min
		long_below = long_below_normalised * (long_max - long_min) + long_min

		short_above = short_above_normalised * (short_max - short_min) + short_min
		short_below = short_below_normalised * (short_max - short_min) + short_min

		#Enter long position 
		if long_price[-2] < long_below and long_price[-1] >= long_below and enter_long_position == False:
			enter_long_position = True
			#Place order for long position
			long_xom_position = connection_ib.make_transaction(account_name, long_xom_count, xom_cont, long_xom_position, order_type)
			long_cvx_position = connection_ib.make_transaction(account_name, long_cvx_count, cvx_cont, long_cvx_position, order_type)
			long_bp_position = connection_ib.make_transaction(account_name, long_bp_count, bp_cont, long_bp_position, order_type)
			
			#Initialised stop loss
			long_stop_loss = long_below

		#Enter short position
		if short_price[-2] < short_below and short_price[-1] >= short_below and enter_short_position == False:
			enter_short_position = True
			#Place order for short position
			short_xom_position = connection_ib.make_transaction(account_name, short_xom_count, xom_cont, short_xom_position, order_type)
			short_cvx_position = connection_ib.make_transaction(account_name, short_cvx_count, cvx_cont, short_cvx_position, order_type)
			short_bp_position = connection_ib.make_transaction(account_name, short_bp_count, bp_cont, short_bp_position, order_type)
			#Initialised stop loss
			short_stop_loss = short_below

		#Update stop loss
		if enter_long_position:
			long_stop_loss = max(long_stop_loss, long_price[-3])
			if long_price[-1] >= long_above:
				long_stop_loss = max(long_stop_loss, long_above, long_price[-3])

		if enter_short_position:
			short_stop_loss = max(short_stop_loss, short_price[-3])
			if short_price[-1] >= short_above:
				short_stop_loss = max(short_stop_loss, short_above, short_price[-3])

		#Exit position 
		if enter_long_position and long_price[-1] <= long_stop_loss:
			enter_long_position = False
			connection_ib.make_transaction(account_name, long_xom_count, xom_cont, long_xom_position * -1, order_type)
			connection_ib.make_transaction(account_name, long_cvx_count, cvx_cont, long_cvx_position * -1, order_type)
			connection_ib.make_transaction(account_name, long_bp_count, bp_cont, long_bp_position * -1, order_type)

		if enter_short_position and short_price[-1] <= short_stop_loss:
			connection_ib.make_transaction(account_name, short_xom_count, xom_cont, short_xom_position * -1, order_type)
			connection_ib.make_transaction(account_name, short_cvx_count, cvx_cont, short_cvx_position * -1, order_type)
			connection_ib.make_transaction(account_name, short_bp_count, bp_cont, short_bp_position * -1, order_type)

	#Increment count
	long_xom_count = short_xom_count + 1
	long_cvx_count = long_cvx_count  + 1
	long_bp_count = long_bp_count  + 1

	short_xom_count = long_xom_count  + 1
	short_cvx_count = short_cvx_count + 1
	short_bp_count = short_bp_count + 1