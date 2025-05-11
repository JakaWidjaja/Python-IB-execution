#Set directory
import os
os.chdir('/home/lun/Desktop/Folder 2/AlgoTradingPython')

from UDF.TWSWrapper import twsWrapper
from UDF.Contract   import MakeContract
from UDF.Data       import HistoricalData, MarketData
from UDF.Orders     import Orders
from UDF.Positions  import Positions
from UDF.Utilities  import SortMarketData
from UDF.Portfolio  import PortfolioValue

#Models
from Strategy.MeanRevertingPortfolio import MeanRevertingPortfolio

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
clientId = 3

#Login to TWS
tws.Login(host, port, clientId, 2)


#Market Data Type. 1 for live data, 4 for delayed data. 
marketDataType = 4
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
#Contract List
path = os.getcwd() + '/config/'
strategyName = 'MeanRevertingPortfolio'
optionStrat = 'option'
futures = 'futures'

#Create Contract
createContract = MakeContract.MakeContract()
contractDict = createContract.contractObjectList(path + 'oneStock' + '.csv')

from ibapi.contract   import Contract
contract = Contract()
contract.symbol = "AAPL"
contract.secType = "STK"
contract.currency = "USD"
contract.exchange = "SMART"
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
#Get market Data
mktData = MarketData.MarketData()

streamThread = threading.Thread(target = mktData.TickStream, args=(tws, contractDict))
streamThread.start()
time.sleep(1.0)


tws.tickData

    
tws.reqTickByTickData(contract)
tick_data = tws.getTickData()

#Equity Data
streamThread = threading.Thread(target = mktData.GetMarketData, args=(tws, contractDict, marketDataType, 1.0))
streamThread.start()
time.sleep(1.0)

dfMarketData = mktData.SortMarketData(tws.mktDataBid, tws.mktDataAsk, tws.mktDataLast, contractDict, 
                                      tws.mktImpVol, tws.mktDelta, tws.mktGamma, tws.mktVega, tws.mktTheta)
dfMarketData

streamThread = threading.Thread(target = mktData.GetOptMktData, args=(tws, contractDict, marketDataType, 8.0))
streamThread.start()
time.sleep(5.0)

#Option Data
dfMarketData = mktData.SortMktOptionData(contractDict, tws.mktDataBid, tws.mktDataAsk, tws.mktDataLast, 
                                         tws.mktUndPrice, tws.mktOptPrice, tws.mktImpVol, tws.mktDelta, 
                                         tws.mktGamma, tws.mktVega, tws.mktTheta, tws.mktPvDiv)
dfMarketData
dfMarketData.to_csv('/home/lun/Desktop/Folder 2/Strategy Development/Option Distributions/data/' + 'aaplMkt.csv')
#**************************************************************************************
#======================================================================================