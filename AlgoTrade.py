#Set directory
import os
os.chdir('/home/lun/Desktop/Folder 2/AlgoTradingPython')

from UDF.TWSWrapper import twsWrapper
from UDF.Contract   import MakeContract
from UDF.Data       import HistoricalData, MarketData
from UDF.Orders     import Orders
from UDF.Positions  import Positions
from UDF.Utilities  import SortMarketData

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
clientId = 1

#Login to TWS
tws.Login(host, port, clientId, 2)

marketOpenTime = dt.time(23, 30, 0)
marketCloseTime = dt.time(6,0,0)

#Market Data Type. 1 for live data, 4 for delayed data. 
marketDataType = 4
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
#Contract List
path = os.getcwd() + '/config/'
strategyName = 'MeanRevertingPortfolio'

#Create Contract
createContract = MakeContract.MakeContract()
contractDict = createContract.contractObjectList(path + strategyName + '.csv')
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
#Get historical Data
'''
histData = HistoricalData.HistoricalData()
histData.GetHistoricalData(tws, 1, contractDict['WBD'], '1 D', '1 secs')
df = pd.DataFrame(tws.histData[0])
'''

'''
#Get market Data
mktData = MarketData.MarketData()
    
streamThread = threading.Thread(target = mktData.GetMarketData, args=(tws, contractDict, 4, 0.2))
streamThread.start()
time.sleep(0.8)

dfMarketData = mktData.SortMarketData(tws.mktDataBid, tws.mktDataAsk, tws.mktDataLast, contractDict)
'''
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
order = Orders.Orders(tws, 1)

#order.SingleMktOrder(contractDict['MSFT'], 'BUY', 20)
direction = ['BUY', 'BUY', 'BUY']
quantity  = [20, 30, 50]
order.MultiMktOrder(contractDict, direction, quantity)


#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
#Position
pos = Positions.Positions(tws)
print(pos.GetPortPosition(1))



tws.reqAccountValue()
a = tws.dfAccountValues
float(a.loc[a['tag'] == 'CashBalance', 'value'].values[0])
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
#Initiate objects
#Get market Data
mktData = MarketData.MarketData()

#Sort Market Data
sortData = SortMarketData.SortMarketData()

#Initiate the bid, ask and mid dataframe. For sorting
stockNames = list(contractDict.keys())
bidPrices  = pd.DataFrame(columns = stockNames)
askPrices  = pd.DataFrame(columns = stockNames)
midPrices  = pd.DataFrame(columns = stockNames)

#Portfolio selection
numberOfDataToUse      = 3000
numberOfStocksToSelect = 8
numberOfStocksToUse    = 3
signal = MeanRevertingPortfolio.MeanRevertingPortfolio(numberOfStocksToUse, numberOfDataToUse)

#Boolean, enter trading or not
enterTrading = False

#Trading Portfolio
portfolio   = []
longWeights = []
entryPrice  = 0
exitPrice   = 0
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************

#**************************************************************************************
#======================================================================================

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
    
    #Get market data
    streamThread = threading.Thread(target = mktData.GetMarketData, args=(tws, 
                                                                          contractDict, 
                                                                          marketDataType, 
                                                                          0.2))
    streamThread.start()
    time.sleep(0.8)

    dfMarketData = mktData.SortMarketData(tws.mktDataBid, tws.mktDataAsk, tws.mktDataLast, contractDict)
    
    #Separate Market Data and create time seris
    bidPrices, askPrices, midPrices = sortData.SortBidAskMid(dfMarketData, bidPrices, askPrices, midPrices)
    
    #Check if the prices list have enough data for calibration. If not then continue.
    if midPrices < numberOfDataToUse:
        continue
    
    #No positions
    if not enterTrading:
        #Create a list of stocks combination
        stockCombinations = signal.StockSelection(midPrices, numberOfStocksToSelect)
        longPortfolio, shortPortfolio = signal.EntryExitSignal(stockCombinations, midPrices, 'longshort')
        
        if not not longPortfolio:
            stocks       = longPortfolio[1][0]
            weights      = longPortfolio[1][1]
            entryPrice   = longPortfolio[1][2]
            exitPrice    = longPortfolio[1][3]
            enterTrading = True
        
        elif not not shortPortfolio:
            stocks   = shortPortfolio[1][0]
            weights      = shortPortfolio[1][1]
            entryPrice   = shortPortfolio[1][3]
            exitPrice    = shortPortfolio[1][2]
            enterTrading = True
            
        if enterTrading:
            #Get cash amount from portfolio
            tws.reqAccountValue()
            accountValues = tws.dfAccountValues
            cash = accountValues.loc[accountValues['tag'] == 'CashBalance', 'value']
            
            #Cash amount per stocks
            cashAmountPerStocks = (weights * cash).astype(int)
        
    
    #Break the loop if market has closed. 
    if marketOpenTime <= currentTime or currentTime < marketCloseTime:
        pass
    else:
        break
#**************************************************************************************
#======================================================================================