# Set directory
import os
os.chdir('/home/lun/Desktop/Folder 2/AlgoTradingPython')
directory = os.getcwd() 

from UDF.TWSWrapper import twsWrapper
from UDF.Contract   import MakeContract
from UDF.Data       import HistoricalData, MarketData
from UDF.Orders     import Orders
from UDF.Positions  import Positions
from UDF.Utilities  import SortMarketData
from UDF.Portfolio  import PortfolioValue, PortfolioWeightsOH


# Models
from Strategy.MeanRevertingPortfolio import MeanRevertingPortfolio, GenerateSignals
from UDF.TechnicalIndicator          import TechnicalIndicator

# Library
import pandas as pd
import datetime as dt
import threading
import time
import copy
import streamlit as st

#======================================================================================
#**************************************************************************************
# Config
configName       = 'configMeanRevertPortEOD.xlsx'
configTWS        = pd.read_excel(os.getcwd() + '/config/' + configName, 'TWS')
configContracts  = pd.read_excel(os.getcwd() + '/config/' + configName, 'Contracts')
configHistParams = pd.read_excel(os.getcwd() + '/config/' + configName, 'Parameters')
configModel      = pd.read_excel(os.getcwd() + '/config/' + configName, 'Model')
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
# TWS
# TWS object
tws = twsWrapper.twsWrapper()

# Login to TWS
host     = configTWS.loc[configTWS['name'] == 'host'     , 'value'].values[0]
port     = configTWS.loc[configTWS['name'] == 'port'     , 'value'].values[0]
clientId = configTWS.loc[configTWS['name'] == 'client id', 'value'].values[0]
tws.Login(host, port, clientId, 2)

# Set market opening and closing time
marketOpenTime  = configTWS.loc[configTWS['name'] == 'market open time'  , 'value'].values[0]
marketCloseTime = configTWS.loc[configTWS['name'] == 'market close time' , 'value'].values[0]

# Market Data Type. 1 for live data, 4 for delayed data. 
marketDataType = configTWS.loc[configTWS['name'] == 'market data type' , 'value'].values[0]

# Market data
mktData = MarketData.MarketData()
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
# Create Contract
createContract = MakeContract.MakeContract()
contractDict = createContract.contractObjectList(configContracts)
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
# Historical Data
# Initiate historical data object
histData = HistoricalData.HistoricalData()

lookbackPeriod = configHistParams.loc[configHistParams['name'] == 'lookback', 'value'].values[0]
interval       = configHistParams.loc[configHistParams['name'] == 'interval', 'value'].values[0]

data = pd.DataFrame(columns = ['date', 'name', 'open', 'high', 'low', 'close', 'volume'])
count = 1
for name, contract in contractDict.items():
    histData.GetHistoricalData(tws, count, contract, lookbackPeriod, interval)
    time.sleep(3)
    
    try:
        temp = tws.histData[count]
    except:
        continue
    temp.insert(1, 'name', name)
    data = pd.concat([data, temp])
    count += 1
    
data['date'] = pd.to_datetime(data['date'], format = '%Y%m%d').dt.date

# Change data configuration
data = data.pivot(index = 'date', columns = 'name', values = 'close')
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
# Model config
config = {'numCalibrationData' : configModel.loc[configModel['name'] == 'calibration data' , 'value'].values[0],
          'numStocks'          : configModel.loc[configModel['name'] == 'stock combination', 'value'].values[0],
          'stopLossPerc1'      : configModel.loc[configModel['name'] == 'stop loss 1'      , 'value'].values[0],
          'stopLossPerc2'      : configModel.loc[configModel['name'] == 'stop loss 2'      , 'value'].values[0],
          'profitLimit'        : configModel.loc[configModel['name'] == 'profit limit'     , 'value'].values[0]}

# Initialise indicators
hurstMaxLag    = configModel.loc[configModel['name'] == 'hurst lag'              , 'value'].values[0]
varRatioLag    = configModel.loc[configModel['name'] == 'variance ratio lag'     , 'value'].values[0]
doubleSMAShort = configModel.loc[configModel['name'] == 'double SMA short window', 'value'].values[0]
doubleSMALong  = configModel.loc[configModel['name'] == 'double SMA long window' , 'value'].values[0]

indicators = {'hurst'     : TechnicalIndicator.TechnicalIndicator.Create('hurst exponent', maxLag = hurstMaxLag),
              'vr'        : TechnicalIndicator.TechnicalIndicator.Create('variance ratio', lag = varRatioLag),
              'hl'        : TechnicalIndicator.TechnicalIndicator.Create('half-life'),
              'doubleSMA' : TechnicalIndicator.TechnicalIndicator.Create('doublesma', shortWindow = doubleSMAShort, longWindow = doubleSMALong)}
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
# Model Calibration

# Config
stockLongShort = configModel.loc[configModel['name'] == 'long short', 'value'].values[0]

# Portfolio combinations
topStocks          = configModel.loc[configModel['name'] == 'top stocks'       , 'value'].values[0]
stockCombinations  = configModel.loc[configModel['name'] == 'stock combination', 'value'].values[0]
numCalibrationData = configModel.loc[configModel['name'] == 'calibration data' , 'value'].values[0]
longShort          = configModel.loc[configModel['name'] == 'long short'       , 'value'].values[0]

strategy         = MeanRevertingPortfolio.MeanRevertingPortfolio(topStocks, numCalibrationData)

portCombinations = strategy.StockSelection(data, stockCombinations, longShort)
portWeights      = strategy.PortfolioPositions(portCombinations, data, longShort)

# Unique tickers
uniqueTickers = sorted({ticker for group in portCombinations for ticker in group})

# Unique Contracts
uniqueContracts = {ticker: contractDict[ticker] for ticker in uniqueTickers if ticker in contractDict}

# Data containing only unique tickers
uniqueData = data[uniqueTickers]

# Initiate Signal object
money  = configModel.loc[configModel['name'] == 'money', 'value'].values[0]
signal = GenerateSignals.GenerateSignals(configModel, indicators, portWeights, money)
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
# Trading
# While loop to wait until the market open
while True:
    currentTime = dt.datetime.now().time()
    if currentTime >= marketOpenTime or currentTime < marketCloseTime:
        break
    else:
        time.sleep(8)

# Market is Open. Start Trading. 
placeHolder = st.empty()
while True:
    # Time now. Use to break the while loop.
    currentTime = dt.datetime.now().time()
    
    # Copy historical data
    histData = copy.deepcopy(uniqueData)
    
    # Get market data
    streamThread = threading.Thread(target = mktData.GetMarketData, args=(tws, 
                                                                          uniqueContracts, 
                                                                          marketDataType, 
                                                                          3.0))
    streamThread.start()
    time.sleep(3.0)

    marketData = mktData.SortMarketData(tws.mktDataBid, tws.mktDataAsk, tws.mktDataLast, uniqueContracts)
    marketData = marketData[['ticker', 'last']].T
    marketData.columns = marketData.iloc[0]
    marketData = marketData.drop(index = 'ticker')
    
    # Combine with historical data
    combineData = pd.concat([histData, marketData], ignore_index = True)
    
    # Create signals
    signalMeanRevert, signalTrend = signal.Signals(combineData)
    
    # Dashboard
    with placeHolder.container():
        st.subheader(" Mean Reversion Strategy")
        st.dataframe(signalMeanRevert)
        
        st.subheader(" Trending Strategy")
        st.dataframe(signalTrend)
    time.sleep(3)
    
    #Break the loop if market has closed. 
    if marketOpenTime <= currentTime or currentTime < marketCloseTime:
        pass
    else:
        break
#**************************************************************************************
#======================================================================================

