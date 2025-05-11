#Set directory
import os
os.chdir('/home/lun/Desktop/Folder 2/AlgoTradingPython')

from UDF.TWSWrapper import twsWrapper
from UDF.Contract   import MakeContract
from UDF.Data       import HistoricalData

#Library
import pandas as pd
import datetime as dt
import time as time

#======================================================================================
#**************************************************************************************
#TWS object
tws = twsWrapper.twsWrapper()

host = '127.0.0.1'
port = 7497
clientId = 1

#Login to TWS
tws.Login(host, port, clientId, 2)

#Market Data Type. 1 for live data, 4 for delayed data. 
marketDataType = 4

#======================================================================================
#**************************************************************************************
#Contract List
path = os.getcwd() + '/config/'
strategyName = 'sp500'
optionStrat = 'option - ES Mini'
futures = 'futures'


#Create Contract
createContract = MakeContract.MakeContract()
contractDict = createContract.contractObjectList(path + strategyName + '.csv')
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
#Equity hist data
histData = HistoricalData.HistoricalData()

df = pd.DataFrame(columns = ['date', 'name', 'open', 'high', 'low', 'close', 'volume'])
count = 821
for name, contract in contractDict.items():
    print(name)
    histData.GetHistoricalData(tws, count, contract, '5 d', '30 secs')
    time.sleep(5)
    
    temp = tws.histData[count]
    temp.insert(1, 'name', name)
    df = pd.concat([df, temp])
    count += 1
    
df['date'] = pd.to_datetime(df['date'], format = '%Y%m%d').dt.date
df['date'] = pd.to_datetime(df['date'], format = '%Y%m%d %H:%M:%S')

df.to_csv('/home/lun/Desktop/Folder 2/Strategy Development/Mean Revert Portfolio/data/' + 'sp500 US Equity Intra.csv' )
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
histData = HistoricalData.HistoricalData()

histData.GetHistoricalData(tws, 100, contractDict['ES20250321C5865'], '5 D', '1 day')
time.sleep(8)
df225 = pd.DataFrame(tws.histData[100])

histData.GetHistoricalData(tws, 101, contractDict['AAPL20241115.0C230.0'], '5 D', '15 secs')
time.sleep(8)
df230 = pd.DataFrame(tws.histData[101])

histData.GetHistoricalData(tws, 102, contractDict['AAPL20241115.0C235.0'], '5 D', '15 secs')
time.sleep(8)
df235 = pd.DataFrame(tws.histData[102])

histData.GetHistoricalData(tws, 103, contractDict['AAPL20241115.0C240.0'], '5 D', '15 secs')
time.sleep(8)
df240 = pd.DataFrame(tws.histData[103])

histData.GetHistoricalData(tws, 105, contractDict['AAPL20241115.0C245.0'], '5 D', '15 secs')
time.sleep(8)
df245 = pd.DataFrame(tws.histData[105])

histData.GetHistoricalData(tws, 106, contractDict['AAPL'], '5 D', '15 secs')
time.sleep(8)
dfAAPL = pd.DataFrame(tws.histData[106])

#Export to csv
df225.to_csv('/home/lun/Desktop/Folder 2/Strategy Development/Option Distributions/data/' + 'AAPL225.csv')
df230.to_csv('/home/lun/Desktop/Folder 2/Strategy Development/Option Distributions/data/' + 'AAPL230.csv')
df235.to_csv('/home/lun/Desktop/Folder 2/Strategy Development/Option Distributions/data/' + 'AAPL235.csv')
df240.to_csv('/home/lun/Desktop/Folder 2/Strategy Development/Option Distributions/data/' + 'AAPL240.csv')
df245.to_csv('/home/lun/Desktop/Folder 2/Strategy Development/Option Distributions/data/' + 'AAPL245.csv')
dfAAPL.to_csv('/home/lun/Desktop/Folder 2/Strategy Development/Option Distributions/data/' + 'AAPL.csv')
#**************************************************************************************
#======================================================================================

#10/10/2024 ATM Imp Vol 25.7%

import matplotlib.pyplot as plt

plt.plot(list(df['close']))

























