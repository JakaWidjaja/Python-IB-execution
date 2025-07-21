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

# Remove first row 08-07-2020, no data.
data = data.iloc[1:]

#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
# Initialise variables
numCalibrationData = 250 # Calibration historical data
topStocks = 10    # Select the top most volatile stocks
numStocks = 5     # number of stock combinations
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

#hurstExp  = TechnicalIndicator.TechnicalIndicator.Create('hurst exponent', maxLag = 50)
#vRatio    = TechnicalIndicator.TechnicalIndicator.Create('variance ratio', lag = 2)
#hlife     = TechnicalIndicator.TechnicalIndicator.Create('half-life')
#doubleSMA = TechnicalIndicator.TechnicalIndicator.Create('doublesma', shortWindow = 30, longWindow = 50)
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
# Backtesting in sample

# Config
config = {'numCalibrationData' : 250,
          'numStocks'          : 5,
          'stopLossPerc1'      : 0.15,
          'stopLossPerc2'      : 0.05,
          'profitLimit'        : 0.05}

# Initialise indicators
indicators = {'hurst'     : TechnicalIndicator.TechnicalIndicator.Create('hurst exponent', maxLag=50),
              'vr'        : TechnicalIndicator.TechnicalIndicator.Create('variance ratio', lag=2),
              'hl'        : TechnicalIndicator.TechnicalIndicator.Create('half-life'),
              'doubleSMA' : TechnicalIndicator.TechnicalIndicator.Create('doublesma', shortWindow=30, longWindow=50)}


bt = BacktestingInSample(data, config, signal, indicators, dataInSample)

hurstLevel = 0.40
hlLevelLower = 0.0
hlLevelUpper = 100.0
smaMult = 5.0
resTrend, resRevert = bt.Backtest(hurstLevel, hlLevelLower, hlLevelUpper, smaMult)

# Save results
resTrend.to_pickle('InSampleTrend5Stocks10.pkl')
resRevert.to_pickle('InSampleRevert5Stocks10.pkl')
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
# Backtesting Out Sample
# Config
config = {'numCalibrationData' : 250,
          'numStocks'          : 5,
          'stopLossPerc1'      : 0.15,
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
resTrend.to_pickle('OutSampleTrend5Stocks15.pkl')
resRevert.to_pickle('OutSampleRevert5Stocks15.pkl')
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

index = 474

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
storageTrend = pd.read_pickle('OutSampleTrend5Stocks15.pkl')
storageRevert = pd.read_pickle('OutSampleRevert5Stocks15.pkl')
storage = storageRevert

uniqueCounts = storage['date'].value_counts().reset_index()
uniqueCounts.columns = ['date', 'count']
uniqueCounts = uniqueCounts.sort_values('date')

# Group by date and calculate positive and negative pnl counts
pnl_counts = storage.groupby('date')['pnl'].apply(
    lambda x: pd.Series({
        'positive_count': (x > 0).sum(),
        'negative_count': (x < 0).sum(),
        'total_pnl': x.sum()
    })
).reset_index()

# Pivot to wide format
pnl_counts_wide = pnl_counts.pivot(index='date', columns='level_1', values='pnl').reset_index()

# Merge with your original count table
uniqueCounts = pd.merge(uniqueCounts, pnl_counts_wide, on='date', how='left')


index = 260

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

storagePos = storage.loc[storage['direction'] == 'long', ]
storageNeg = storage.loc[storage['direction'] == 'short', ]

import seaborn as sns
plt.figure()
sns.histplot(storagePos['pnl'])
plt.title('P&L Distribution')
plt.xlabel('P&L')
plt.ylabel('Frequency')
plt.show()

import seaborn as sns
plt.figure()
sns.histplot(storageNeg['pnl'])
plt.title('P&L Distribution')
plt.xlabel('P&L')
plt.ylabel('Frequency')
plt.show()
#**************************************************************************************
#======================================================================================

a = storage.loc[:, 'info'][0]

