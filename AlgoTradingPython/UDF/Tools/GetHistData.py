#Set directory
import os
os.chdir('/home/lun/Desktop/Folder 2/AlgoTradingPython')

from UDF.TWSWrapper import twsWrapper
from UDF.Contract   import MakeContract
from UDF.Data       import HistoricalData

#Library
from threading import Event
import pandas as pd
import datetime as dt
import time as time
import matplotlib.pyplot as plt
import pickle

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

duration = '3 M' #'5 Y' # '10 D'
intervals = '2 mins' #'1 day'# '30 secs
timeDelay = 30
count = 150  # IB historical data request ID
for name, contract in contractDict.items():
    print(f"Requesting data for: {name}")
    histData.GetHistoricalData(tws, count, contract, duration, intervals)

    # Wait for the data to arrive or timeout
    timeout = 160  # seconds
    start_time = time.time()
    while count not in tws.histData:
        if time.time() - start_time > timeout:
            print(f"Timeout waiting for {name} (request ID {count})")
            break
        time.sleep(timeDelay)

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
df.to_csv('/home/lun/Desktop/Folder 2/Strategy Development/Mean Revert Portfolio/data/' + 'sp500 US Equity.csv' )
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
histData = HistoricalData.HistoricalData()

path = os.getcwd() + '/config/'
strategyName = 'VIXFutures'
strategyName = 'VIXOptions'

contractList = pd.read_excel(path + strategyName + '.xlsx', sheet_name = 'Contracts')

#Create Contract
createContract = MakeContract.MakeContract()
contractDict = createContract.contractObjectList(contractList)


res = {}
endDate = pd.to_datetime('20251113 08:14:45', format="%Y%m%d %H:%M:%S")
endDate = endDate.strftime("%Y%m%d %H:%M:%S") 
for name, contract in contractDict.items():
    
    reqId = tws.getNextReqId()
    tws.histData[reqId] = None
    tws.histDataComplete[reqId] = Event()

    histData.GetHistoricalData(tws, reqId, contract, "8 D", "15 secs", endDateTime = endDate)

    # WAIT HERE until IB signals completion
    time.sleep(38)
    #tws.histDataComplete[reqId].wait(timeout = 38)   

    # NOW the data is definitely ready
    data = tws.histData[reqId]
    print(name, " done download")
    
    res[name] = data
    #print(res)
    time.sleep(10)


# Save 
df = pd.DataFrame()
for name, data in res.items():
    expiry = pd.to_datetime(name[3 : 11]).date()
    if name[11] == 'C':
        putCall = 'call'
    else:
        putCall = 'put'
    strike = float(name[12:])
    
    prices = data.loc[:, ['date', 'close']]   
    prices['date'] = pd.to_datetime(prices['date'], format = "%Y%m%d %H:%M:%S")
    date = prices['date'].dt.date
    time = prices['date'].dt.time
    
    prices['date'] = date
    prices.insert(1, 'time', time)
    prices.insert(2, 'expiry', expiry)
    prices.insert(3, 'put/call', putCall)
    prices.insert(4, 'strike', strike)

    df = pd.concat([df, prices], ignore_index = True)
# Save
path = '/home/lun/Desktop/Folder 2/Strategy Development/Option Risk Neutral/data/VIXOption_' + str(expiry) + '_3.pkl'
df.to_pickle(path)



s = 28
reqId = tws.getNextReqId()
histData.GetHistoricalData(tws, 50086, contractDict['VIX20260121'], '8 D', '15 secs', endDateTime = endDate)
time.sleep(s)
VIXFutures = pd.DataFrame(tws.histData[50086])
VIXFutures.to_pickle('/home/lun/Desktop/Folder 2/Strategy Development/Option Risk Neutral/data/' + 'VIX_Futures_3.csv')



#**************************************************************************************
#======================================================================================





















