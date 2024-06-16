#Set directory
import os
os.chdir('/home/lun/Desktop/Folder 2/AlgoTradingPython')

from UDF.TWSWrapper import twsWrapper
from UDF.Contract   import MakeContract
from UDF.Data       import HistoricalData, MarketData
from UDF.Orders     import Orders
from UDF.Positions  import Positions

import pandas as pd
import datetime as dt
import threading
import time
#======================================================================================
#**************************************************************************************
#TWS object
tws = twsWrapper.twsWrapper()

host = '127.0.0.1'
port = 7497
clientId = 2

#Login to TWS
tws.Login(host, port, clientId, 1)

marketOpenTime = dt.time(23, 30, 0)
marketCloseTime = dt.time(6,0,0)
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
#Contract List
path = os.getcwd() + '/config/'
strategyName = 'MeanRevertingPortfolio'

#Create Contract
createContract = MakeContract.MakeContract()
contractList = createContract.contractObjectList(path + strategyName + '.csv')
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
#Get historical Data
'''
histData = HistoricalData.HistoricalData()
histData.GetHistoricalData(tws, 1, contractList['WBD'], '1 D', '1 secs')
df = pd.DataFrame(tws.histData[0])
'''


#Get market Data
mktData = MarketData.MarketData()
    
streamThread = threading.Thread(target = mktData.GetMarketData, args=(tws, contractList, 4, 0.2))
streamThread.start()
time.sleep(0.8)

dfMarketData = mktData.SortMarketData(tws.mktDataBid, tws.mktDataAsk, tws.mktDataLast, contractList)

#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
#order = Orders.Orders(tws, 1)

#order.SingleMktOrder(contractList['MSFT'], 'BUY', 20)
#direction = ['BUY', 'BUY', 'BUY']
#quantity  = [20, 30, 50]
#order.MultiMktOrder(contractList, direction, quantity)


#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
#Position
pos = Positions.Positions(tws)
print(pos.GetPortPosition(1))
#**************************************************************************************
#======================================================================================
a = dt.time(3,45)
#======================================================================================
#**************************************************************************************
#Trading
#While loop to wait until the market open
while True:
    currentTime = dt.datetime.now().time()
    if currentTime >= marketOpenTime or currentTime < marketCloseTime:
        break
    else:
        time.sleep(8)

#Market is Open. Start Trading. 
while True:
    #Time now. Use to break the while loop.
    currentTime = dt.datetime.now().time()
    
    
    
    
    
    
    if marketOpenTime <= currentTime or currentTime < marketCloseTime:
        pass
    else:
        break
#**************************************************************************************
#======================================================================================
