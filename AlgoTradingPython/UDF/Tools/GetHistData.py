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
strategyName = 'configMeanRevertPortEOD'

contractList = pd.read_excel(path + strategyName + '.xlsx', sheet_name = 'Contracts')

#Create Contract
createContract = MakeContract.MakeContract()
contractDict = createContract.contractObjectList(contractList)
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
#Equity hist data
histData = HistoricalData.HistoricalData()

# Create master DataFrame with correct structure
df = pd.DataFrame(columns=['date', 'time', 'name', 'open', 'high', 'low', 'close', 'volume'])

count = 200  # IB historical data request ID
for name, contract in contractDict.items():
    print(f"Requesting data for: {name}")
    histData.GetHistoricalData(tws, count, contract, '5 D', '30 secs')

    # Wait for the data to arrive or timeout
    timeout = 30  # seconds
    start_time = time.time()
    while count not in tws.histData:
        if time.time() - start_time > timeout:
            print(f"Timeout waiting for {name} (request ID {count})")
            break
        time.sleep(0.5)

    if count in tws.histData:
        temp = tws.histData[count]

        # Add stock name column
        temp['name'] = name

        # Handle missing 'time' by splitting 'date' if needed
        if 'date' in temp.columns and 'time' not in temp.columns:
            if temp['date'].dtype == object or pd.api.types.is_string_dtype(temp['date']):
                try:
                    dt_split = temp['date'].str.split(" ", n=1, expand=True)
                    if dt_split.shape[1] == 2:
                        temp['date'] = dt_split[0]
                        temp['time'] = dt_split[1]
                    else:
                        temp['time'] = ""
                except Exception as e:
                    print(f"Couldn't split datetime for {name}: {e}")
                    temp['time'] = ""
            else:
                temp['time'] = ""

        # Ensure all required columns are present
        expected_cols = ['date', 'time', 'name', 'open', 'high', 'low', 'close', 'volume']
        for col in expected_cols:
            if col not in temp.columns:
                temp[col] = None  # Fill missing columns with NaN

        # Reorder and append
        temp = temp[expected_cols]
        df = pd.concat([df, temp], ignore_index=True)

        # remove entry to save memory
        del tws.histData[count]
    else:
        print(f"No data received for {name}")

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

























