#Set directory
import os
os.chdir('/home/lun/Desktop/Folder 2/Strategy Development/Mean Revert Portfolio')
directory = os.getcwd()

import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt

from UDF.MeanRevertingPortfolio import MeanRevertingPortfolio
from UDF.TechnicalIndicator     import TechnicalIndicator
from BacktestingInSample        import BacktestingInSample
from BacktestingOutSample       import BacktestingOutSample

#======================================================================================
#**************************************************************************************
# Import data
data = pd.read_csv(directory + '/data/sp500 US Equity.csv')
data['date'] = pd.to_datetime(data['date'], format = '%Y-%m-%d').dt.date

# Change data configuration
data = data.pivot(index = 'date', columns = 'name', values = 'close')

# index to column
data = data.reset_index()

# Remove KVUE
data = data.drop(['KVUE'], axis = 1)

# Remove dates
dateLimit = dt.datetime(2020, 3, 19).date()
data = data.loc[data['date']>= dateLimit]
data = data.reset_index(drop = True)
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
# Initialise variables
numCalibrationData = 250 # Calibration historical data
topStocks = 10    # Select the top most volatile stocks
numStocks = 3     # number of stock combinations
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
# Separate date into in-sample and out-sample
numInSample = 501
numOutSample = len(data) - numInSample

dataInSample  = 250
dataOutSample = data.iloc[(numInSample - numCalibrationData) :, :]
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
# initialise object
signal = MeanRevertingPortfolio(topStocks, numCalibrationData)

hurstExp  = TechnicalIndicator.TechnicalIndicator.Create('hurst exponent', maxLag = 50)
vRatio    = TechnicalIndicator.TechnicalIndicator.Create('variance ratio', lag = 2)
hlife     = TechnicalIndicator.TechnicalIndicator.Create('half-life')
doubleSMA = TechnicalIndicator.TechnicalIndicator.Create('doublesma', shortWindow = 30, longWindow = 50)
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
# Backtesting in sample

# Config
config = {'numCalibrationData' : 250,
          'numStocks'          : 3,
          'stopLossPerc1'      : 0.20,
          'stopLossPerc2'      : 0.05,
          'profitLimit'        : 0.05}

# Initialise indicators
indicators = {'hurst'     : TechnicalIndicator.TechnicalIndicator.Create('hurst exponent', maxLag=50),
              'vr'        : TechnicalIndicator.TechnicalIndicator.Create('variance ratio', lag=2),
              'hl'        : TechnicalIndicator.TechnicalIndicator.Create('half-life'),
              'doubleSMA' : TechnicalIndicator.TechnicalIndicator.Create('doublesma', shortWindow=30, longWindow=50)}

bt = BacktestingInSample(data, config, signal, indicators, dataInSample)
resTrend, resRevert = bt.Backtest()

# Save results
resTrend.to_pickle('InSampleTrend.pkl')
resRevert.to_pickle('InSampleRevert.pkl')
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
# Backtesting Out Sample
# Config
config = {'numCalibrationData' : 250,
          'numStocks'          : 3,
          'stopLossPerc1'      : 0.20,
          'stopLossPerc2'      : 0.05,
          'profitLimit'        : 0.05}

# Initialise indicators
indicators = {'hurst'     : TechnicalIndicator.TechnicalIndicator.Create('hurst exponent', maxLag=50),
              'vr'        : TechnicalIndicator.TechnicalIndicator.Create('variance ratio', lag=2),
              'hl'        : TechnicalIndicator.TechnicalIndicator.Create('half-life'),
              'doubleSMA' : TechnicalIndicator.TechnicalIndicator.Create('doublesma', shortWindow=30, longWindow=50)}
bt = BacktestingOutSample(dataOutSample, config, signal, indicators)
resTrend, resRevert  = bt.Backtest()

# Save results
resTrend.to_pickle('OutSampleTrend.pkl')
resRevert.to_pickle('OutSampleRevert.pkl')
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
# Plotting in Sample
storage = pd.read_pickle('InSample20.pkl')
storageTrend = resTrend
storageRevert = resRevert

storage = storageRevert

storage = storage.loc[
                      (storage['vr']    > 1.0) &
                      (storage['hurst'] > 0.55)   &
                      (storage['hl']    < 0.0), :]
storage = storage.reset_index(drop = True)

storage = storage.loc[   (storage['hurst'] < 0.40)  &
                      (storage['hl']    > 0.0)  &  (storage['hl']    < 100.0), :]
storage = storage.reset_index(drop = True)

index = 522

info = storage.iloc[index, storage.columns.get_loc('info')]
historyTS = storage.iloc[index, storage.columns.get_loc('history')]
futureTS = storage.iloc[index, storage.columns.get_loc('future')]

combineHistFut = pd.concat([historyTS, futureTS], ignore_index = True)[:350]
df = doubleSMA.Calculate(historyTS)

combineHistFut.plot(x = 'date', y = 'total')
cutoff = historyTS['date'].iloc[-1]
plt.plot(df['date'], df['sma short'], label='Short SMA', color='blue')
plt.plot(df['date'], df['sma long'], label='Long SMA', color='red')
plt.axvline(x=cutoff, color='red', linestyle='--')
plt.legend()
plt.show()

pnl = storage['pnl']  
hurst = storage['hurst']
vr = storage['vr']
hl = storage['hl']
theta = storage['theta']
sigma = storage['sigma']
midDiff = storage['mid diff']

plt.scatter(pnl, midDiff)  
plt.xlabel('pnl')
plt.show()

# Histogram
import seaborn as sns
plt.figure()
sns.histplot(storage['pnl'])
plt.title('P&L Distribution')
plt.xlabel('P&L')
plt.ylabel('Frequency')
plt.show()
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
# Plotting out Sample
storage = pd.read_pickle('OutSample.pkl')
storageTrend = resTrend
storageRevert = resRevert
storage = storageRevert


index = 9331

info = storage.iloc[index, storage.columns.get_loc('info')]
historyTS = storage.iloc[index, storage.columns.get_loc('history')]
futureTS = storage.iloc[index, storage.columns.get_loc('future')]

combineHistFut = pd.concat([historyTS, futureTS], ignore_index = True)
df = doubleSMA.Calculate(historyTS)


combineHistFut.plot(x = 'date', y = 'total')
cutoff = list(historyTS['date'])[-1]
plt.plot(df['date'], df['sma short'], label='Short SMA', color='blue')
plt.plot(df['date'], df['sma long'], label='Long SMA', color='red')
plt.axvline(x=cutoff, color='red', linestyle='--')
plt.legend()
plt.show()

import seaborn as sns
plt.figure()
sns.histplot(storage['pnl'])
plt.title('P&L Distribution')
plt.xlabel('P&L')
plt.ylabel('Frequency')
plt.show()
#**************************************************************************************
#======================================================================================


storageRevert.iloc[0, 1]
names = storageRevert.iloc[0, 1][0]
weights = storageRevert.iloc[0, 1][1]
hist = storageRevert.iloc[0, 2]
date = storageRevert.iloc[0, 0]
portPrice = storageRevert.iloc[0, 0]
prices = data.loc[data['date'] == date, names]

dollarWeights = weights * 1000
dollarWeights / prices

57.89*1.4727 + 11.48258*35.74 + 9.781463*50.54

989.9971522200001/44.58750750369989
