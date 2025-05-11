#Set directory
import os
os.chdir('/home/lun/Desktop/Folder 2/AlgoTradingPython')

from UDF.TWSWrapper import twsWrapper
from UDF.Positions  import Positions


#Library
import pandas as pd
import datetime as dt
import threading
import time
from itertools import combinations
#======================================================================================
#**************************************************************************************
#TWS object
tws = twsWrapper.twsWrapper()

host = '127.0.0.1'
port = 7497
clientId = 9

#Login to TWS
tws.Login(host, port, clientId, 2)

marketOpenTime = dt.time(10, 30, 0)
marketCloseTime = dt.time(16,0,0)

#Market Data Type. 1 for live data, 4 for delayed data. 
marketDataType = 4
#**************************************************************************************
#======================================================================================

tws.reqAccountValue()
balances = tws.dfAccountValues

print(balances)
