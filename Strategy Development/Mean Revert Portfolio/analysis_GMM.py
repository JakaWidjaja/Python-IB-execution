#Set directory
import os
os.chdir('/home/lun/Desktop/Folder 2/Strategy Development/Mean Revert Portfolio')
directory = os.getcwd()

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import optuna
import seaborn as sns

from UDF.MeanRevertingPortfolio import MeanRevertingPortfolio
from UDF.TechnicalIndicator     import TechnicalIndicator
from UDF.GaussianMixModel       import GaussianMixtureModel
from BacktestingInSample_MeanRevert        import BacktestingInSample_MeanRevert
from BacktestingOutSample_MeanRevert       import BacktestingOutSample_MeanRevert

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
numCalibrationData = 200 # Calibration historical data
topStocks = 8    # Select the top most volatile stocks
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
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
# Backtesting in sample

# Config
config = {'numCalibrationData' : 200,
          'numStocks'          : 5,
          'stopLossPerc1'      : 0.20,
          'stopLossPerc2'      : 0.05,
          'profitLimit'        : 0.05}

# Initialise indicators
indicators = {'hurst'     : TechnicalIndicator.TechnicalIndicator.Create('hurst exponent', maxLag=50),
              'vr'        : TechnicalIndicator.TechnicalIndicator.Create('variance ratio', lag=2),
              'hl'        : TechnicalIndicator.TechnicalIndicator.Create('half-life'),
              'doubleSMA' : TechnicalIndicator.TechnicalIndicator.Create('doublesma', shortWindow=30, longWindow=50)}
btInSample = BacktestingInSample_MeanRevert(data, config, signal, indicators, dataInSample)

# optimisation
numClusters = 2
def objective(trial):
    # Sample parameters
    hurst = trial.suggest_float('hurstLevel', 0.0, 0.4)
    hl_upper = trial.suggest_float('hlLevelUpper', 0, 100.0)
    sma_mult = trial.suggest_float('smaMult', 1.0, 5.0)

    res = bt.Backtest(hurst, 0, hl_upper, sma_mult)
    rets = res['return'].dropna().values

    if len(rets) < 10:
        return float('inf')  # penalize bad runs
    
    gmm = GaussianMixtureModel.GaussianMixtureModel(numClusters=2)
    gmm.Fit(pd.Series(rets))
    means, vol, weights = gmm.Params()

    # Sort to ensure mean[1] is best
    if means[1] < means[0]:
        means = means[::-1]
        weights = weights[::-1]
    
    lambda_weight = 3.0
    gamma_penalty = 2.0
    
    score = -(means[1] + lambda_weight * weights[1] - gamma_penalty * abs(min(0, means[0])))

    return score

    
study = optuna.create_study(direction="minimize")  # minimize negative objective
study.optimize(objective, n_trials=30, n_jobs=-1)
study.best_params

# Optimisation results
hurstLevel = study.best_params['hurstLevel']
hlLevelUpper = study.best_params['hlLevelUpper']
smaMult = study.best_params['smaMult']

hurstLevel = 0.3617029216013116
hlLevelLower = 0
hlLevelUpper = 62.35711188120264
smaMult = 3.028434092461338

# Calculate in-sample back-testing
resInSample = btInSample.Backtest(hurstLevel, hlLevelLower, hlLevelUpper, smaMult)

# Get the GMM results
gmm = GaussianMixtureModel.GaussianMixtureModel(numClusters)
gmm.Fit(resInSample['return'])
mean, vol, weights = gmm.Params()

# Save results
resInSample.to_pickle('InSample.pkl')
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
# Backtesting Out Sample
# Config
config = {'numCalibrationData' : 200,
          'numStocks'          : 5,
          'stopLossPerc1'      : 0.20,
          'stopLossPerc2'      : 0.05,
          'profitLimit'        : 0.05}

# Initialise indicators
indicators = {'hurst'     : TechnicalIndicator.TechnicalIndicator.Create('hurst exponent', maxLag=50),
              'vr'        : TechnicalIndicator.TechnicalIndicator.Create('variance ratio', lag=2),
              'hl'        : TechnicalIndicator.TechnicalIndicator.Create('half-life'),
              'doubleSMA' : TechnicalIndicator.TechnicalIndicator.Create('doublesma', shortWindow=30, longWindow=50)}
bt = BacktestingOutSample_MeanRevert(dataOutSample, config, signal, indicators)

hurstLevel = 0.3617029216013116
hlLevelLower = 0
hlLevelUpper = 62.35711188120264
smaMult = 2.028434092461338

resOutSample = bt.Backtest(hurstLevel, hlLevelLower, hlLevelUpper, smaMult)

gmm = GaussianMixtureModel.GaussianMixtureModel(numClusters)
gmm.Fit(resOutSample['return'])
mean, vol, weights = gmm.Params()

# Save results
resOutSample.to_pickle('OutSample.pkl')
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
# Plotting in Sample
# Histogram
plt.figure()
sns.histplot(resInSample['return']*100)
plt.title('Return Distribution')
plt.xlabel('Return %')
plt.ylabel('Frequency')
plt.tight_layout()
plt.show()

dailyPnl = resInSample.groupby('date')['pnl'].sum().reset_index()
dailyPnl['cumulative pnl'] = dailyPnl['pnl'].cumsum()

plt.plot(dailyPnl['date'], dailyPnl['cumulative pnl'], marker='o')
plt.xlabel('Date')
plt.ylabel('Cumulative PnL')
plt.title('Cumulative PnL Over Time')
plt.grid(True)
plt.tight_layout()
plt.show()
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
# Plotting out Sample
plt.figure()
sns.histplot(resOutSample['return']*100)
plt.title('Return Distribution')
plt.xlabel('Return %')
plt.ylabel('Frequency')
plt.show()

dailyPnl = resOutSample.groupby('date')['pnl'].sum().reset_index()
dailyPnl['cumulative pnl'] = dailyPnl['pnl'].cumsum()

plt.plot(dailyPnl['date'], dailyPnl['cumulative pnl'], marker='o')
plt.xlabel('Date')
plt.ylabel('Cumulative PnL')
plt.title('Cumulative PnL Over Time')
plt.grid(True)
plt.tight_layout()
plt.show()
#**************************************************************************************
#======================================================================================