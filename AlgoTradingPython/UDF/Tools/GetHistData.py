#Set directory
import os
os.chdir('/home/lun/Desktop/Folder 2/AlgoTradingPython')

from UDF.TWSWrapper import twsWrapper
from UDF.Contract   import MakeContract
from UDF.Data       import HistoricalData
from ibapi.contract import Contract

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
clientId = 2

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
'''
#======================================================================================
#**************************************************************************************
#Equity hist data
histData = HistoricalData.HistoricalData()

# Create master DataFrame with correct structure
df = pd.DataFrame(columns=['date', 'time', 'name', 'open', 'high', 'low', 'close', 'volume'])

duration = '3 M' #'5 Y' # '10 D'
intervals = '15 Secs' #'1 day'# '30 secs
timeDelay = 30
count = 100  # IB historical data request ID
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
'''
#======================================================================================
#**************************************************************************************
histData = HistoricalData.HistoricalData()

path = os.getcwd() + '/config/'
number = 6
strategyName = 'ESOptions_OS' + str(number) #Change title
contractList = pd.read_excel(path + strategyName + '.xlsx', sheet_name = 'Contracts')

#Create Contract
createContract = MakeContract.MakeContract()
contractDict = createContract.contractObjectList(contractList)

res = {}
endDate = pd.to_datetime('202601' + str(number) + ' 10:00:00', format="%Y%m%d %H:%M:%S") #Change Date
endDate = endDate.strftime("%Y%m%d %H:%M:%S") 
for name, contract in contractDict.items():
    
    reqId = tws.getNextReqId()
    tws.histData[reqId] = None
    tws.histDataComplete[reqId] = Event()

    histData.GetHistoricalData(tws, reqId, contract, "1 D", "15 secs", endDateTime = endDate)

    # WAIT HERE until IB signals completion
    time.sleep(28)
    #tws.histDataComplete[reqId].wait(timeout = 38)   

    # NOW the data is definitely ready
    data = tws.histData[reqId]
    print(name, " done download")
    
    res[name] = data
    #print(res)
    time.sleep(5)


# Save 
df = pd.DataFrame()
for name, data in res.items():
    expiry = pd.to_datetime(name[2 : 10]).date()
    if name[10] == 'C':
        putCall = 'call'
    else:
        putCall = 'put'
    strike = float(name[11:])
    
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
path = '/home/lun/Desktop/Folder 2/Strategy Development/Option Risk Neutral/data/ESOption_OS_' + str(number) + '.pkl'
df.to_pickle(path)

# Checking
path17 ='/home/lun/Desktop/Folder 2/Strategy Development/Option Risk Neutral/data/' + 'ESOption_OS_17.pkl'
path16 ='/home/lun/Desktop/Folder 2/Strategy Development/Option Risk Neutral/data/' + 'ESOption_OS_16.pkl'
path15 ='/home/lun/Desktop/Folder 2/Strategy Development/Option Risk Neutral/data/' + 'ESOption_OS_15.pkl'
path14 ='/home/lun/Desktop/Folder 2/Strategy Development/Option Risk Neutral/data/' + 'ESOption_OS_14.pkl'
path13 ='/home/lun/Desktop/Folder 2/Strategy Development/Option Risk Neutral/data/' + 'ESOption_OS_13.pkl'
path10 ='/home/lun/Desktop/Folder 2/Strategy Development/Option Risk Neutral/data/' + 'ESOption_OS_10.pkl'
path9 ='/home/lun/Desktop/Folder 2/Strategy Development/Option Risk Neutral/data/' + 'ESOption_OS_9.pkl'
path8 ='/home/lun/Desktop/Folder 2/Strategy Development/Option Risk Neutral/data/' + 'ESOption_OS_8.pkl'
path7 ='/home/lun/Desktop/Folder 2/Strategy Development/Option Risk Neutral/data/' + 'ESOption_OS_7.pkl'
path6 ='/home/lun/Desktop/Folder 2/Strategy Development/Option Risk Neutral/data/' + 'ESOption_OS_6.pkl'
with open(path17, 'rb') as f:
    optionPrice17 = pickle.load(f)
with open(path16, 'rb') as f:
    optionPrice16 = pickle.load(f)
with open(path15, 'rb') as f:
    optionPrice15 = pickle.load(f)
with open(path14, 'rb') as f:
    optionPrice14 = pickle.load(f)   
with open(path13, 'rb') as f:
    optionPrice13 = pickle.load(f)      
with open(path10, 'rb') as f:
    optionPrice10 = pickle.load(f)  
with open(path9, 'rb') as f:
    optionPrice9 = pickle.load(f)   
with open(path8, 'rb') as f:
    optionPrice8 = pickle.load(f)     
with open(path7, 'rb') as f:
    optionPrice7 = pickle.load(f)
with open(path6, 'rb') as f:
    optionPrice6 = pickle.load(f)  
    
t = dt.time(2,7,30)
optionPrice17.loc[optionPrice17['time'] == t, :]
optionPrice16.loc[optionPrice16['time'] == t, :]
optionPrice15.loc[optionPrice15['time'] == t, :]
optionPrice14.loc[optionPrice14['time'] == t, :]
optionPrice13.loc[optionPrice13['time'] == t, :]
optionPrice10.loc[optionPrice10['time'] == t, :]
optionPrice9.loc[optionPrice9['time'] == t, :]
optionPrice8.loc[optionPrice8['time'] == t, :]
optionPrice7.loc[optionPrice7['time'] == t, :]
optionPrice6.loc[optionPrice6['time'] == t, :]
#============================================================================
#============================================================================
# Futures
histData = HistoricalData.HistoricalData()

path = os.getcwd() + '/config/'
strategyName = 'SPXFutures'
contractList = pd.read_excel(path + strategyName + '.xlsx', sheet_name = 'Contracts')

#Create Contract
createContract = MakeContract.MakeContract()
contractDict = createContract.contractObjectList(contractList)

endDate = pd.to_datetime('20260107 10:00:00', format="%Y%m%d %H:%M:%S")
endDate = endDate.strftime("%Y%m%d %H:%M:%S") 

c = Contract()
c.symbol   = "ES"
c.secType  = "FUT"
c.exchange = "CME"        # if this fails, try "GLOBEX"
c.currency = "USD"
c.lastTradeDateOrContractMonth = "202603"  

s = 38
reqId = tws.getNextReqId()
histData.GetHistoricalData(tws, 11023, c, '8 D', '15 secs', endDateTime = endDate)
time.sleep(s)
SPXFutures = pd.DataFrame(tws.histData[11023])
SPXFutures.to_pickle('/home/lun/Desktop/Folder 2/Strategy Development/Option Risk Neutral/data/' + 'ESFutures_OS_1.pkl')



#**************************************************************************************
#======================================================================================
path1 ='/home/lun/Desktop/Folder 2/Strategy Development/Option Risk Neutral/data/' + 'SPX_Futures_1.pkl'
path2 ='/home/lun/Desktop/Folder 2/Strategy Development/Option Risk Neutral/data/' + 'SPX_Futures_2.pkl'
path3 ='/home/lun/Desktop/Folder 2/Strategy Development/Option Risk Neutral/data/' + 'SPX_Futures_3.pkl'
path4 ='/home/lun/Desktop/Folder 2/Strategy Development/Option Risk Neutral/data/' + 'SPX_Futures_4.pkl'
path5 ='/home/lun/Desktop/Folder 2/Strategy Development/Option Risk Neutral/data/' + 'SPX_Futures_5.pkl'
pathIS ='/home/lun/Desktop/Folder 2/Strategy Development/Option Risk Neutral/data/' + 'ESFutures_IS.pkl'
pathOS ='/home/lun/Desktop/Folder 2/Strategy Development/Option Risk Neutral/data/' + 'ESFutures_OS.pkl'
pathOS2 ='/home/lun/Desktop/Folder 2/Strategy Development/Option Risk Neutral/data/' + 'ESFutures_OS_1.pkl'

with open(path1, 'rb') as f:
    futuresPrice1 = pickle.load(f)
with open(path2, 'rb') as f:
    futuresPrice2 = pickle.load(f)
with open(path3, 'rb') as f:
    futuresPrice3 = pickle.load(f)
with open(path4, 'rb') as f:
    futuresPrice4 = pickle.load(f)
with open(path5, 'rb') as f:
    futuresPrice5 = pickle.load(f)
    
with open(pathIS, 'rb') as f:
    futuresPriceIS = pickle.load(f)
with open(pathOS, 'rb') as f:
    futuresPriceOS = pickle.load(f)
with open(pathOS2, 'rb') as f:
    futuresPriceOS2 = pickle.load(f)

futuresPriceIS['date'] = pd.to_datetime(futuresPriceIS['date'], format = "%Y%m%d %H:%M:%S")
date = futuresPriceIS['date'].dt.date
Time = futuresPriceIS['date'].dt.time
futuresPriceIS['date'] = date
futuresPriceIS.insert(1, 'time', Time)

plt.plot(futuresPriceIS['close'])

date = futuresPriceIS['date']
date = sorted(list(set(date)))

num = 3
min(futuresPriceIS.loc[futuresPriceIS['date'] == date[num],'close'])
max(futuresPriceIS.loc[futuresPriceIS['date'] == date[num],'close'])

plt.plot(futuresPriceIS.loc[futuresPriceIS['date'] == date[num],'close'])

# Out of sample
futuresPriceOS['date'] = pd.to_datetime(futuresPriceOS['date'], format = "%Y%m%d %H:%M:%S")
date = futuresPriceOS['date'].dt.date
Time = futuresPriceOS['date'].dt.time
futuresPriceOS['date'] = date
futuresPriceOS.insert(1, 'time', Time)

futuresPriceOS2['date'] = pd.to_datetime(futuresPriceOS2['date'], format = "%Y%m%d %H:%M:%S")
date = futuresPriceOS2['date'].dt.date
Time = futuresPriceOS2['date'].dt.time
futuresPriceOS2['date'] = date
futuresPriceOS2.insert(1, 'time', Time)

futuresPricesOSComb = pd.concat([futuresPriceOS2, futuresPriceOS], ignore_index = True)
futuresPricesOSComb.to_pickle('/home/lun/Desktop/Folder 2/Strategy Development/Option Risk Neutral/data/' + 'ESFutures_OS.pkl')

plt.plot(futuresPricesOSComb['close'])

date = futuresPricesOSComb['date']
date = sorted(list(set(date)))

num = 6
min(futuresPricesOSComb.loc[futuresPricesOSComb['date'] == date[num],'close'])
max(futuresPricesOSComb.loc[futuresPricesOSComb['date'] == date[num],'close'])





