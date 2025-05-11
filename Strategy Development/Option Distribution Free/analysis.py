#Set directory
import os
os.chdir('/home/lun/Desktop/Folder 2/Strategy Development/Option Distribution Free')
directory = os.getcwd()

from UDF.OptionPricer import Black76
from UDF.OptionPricer import BlackScholes
from UDF.OptionPricer import OptionUpperLowerBound

import pandas   as pd
import numpy    as np
import datetime as dt
from scipy.optimize import minimize
import matplotlib.pyplot as plt
#======================================================================================
#**************************************************************************************
#import data

optData = pd.read_csv(directory + '/data/E-Mini Options March 2025.csv')
optData['Expiry']     = pd.to_datetime(optData['Expiry']    , format = '%d-%m-%Y').dt.date
optData['Value Date'] = pd.to_datetime(optData['Value Date'], format = '%d-%m-%Y').dt.date
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
#Treasury yield
days30 = 0.0442
days60 = 0.0435
days90 = 0.0436
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
#Black76 price
bl = Black76.Black76()

valueDate  = optData['Value Date'][0]
expiryDate = optData['Expiry'][0]
underlyingPrice = optData['Underlying Price'][0]
expiry = (expiryDate - valueDate).days / 365.0
rate = days60

optData['Model Price'] = 0.0
for i in range(len(optData)):
    strike      = optData.iloc[i, optData.columns.get_loc('Strike')]
    impVol      = optData.iloc[i, optData.columns.get_loc('Implied Vol')] / 100.0
    optType     = optData.iloc[i, optData.columns.get_loc('Type')]
    
    modelPrice = bl.Price(underlyingPrice, strike, impVol, expiry, rate, optType)
    
    optData.iloc[i, optData.columns.get_loc('Model Price')] = modelPrice
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
opt = OptionUpperLowerBound.OptionUpperLowerBound()

index = 20
price = underlyingPrice
strike = optData.iloc[index, optData.columns.get_loc('Strike')]
vol = optData.iloc[index, optData.columns.get_loc('Implied Vol')]
rate = days60
expiry = (expiryDate - valueDate).days / 365.0

opt.TwoMomentsMode(price, strike, vol, rate, expiry)
opt.ThreeMoments(price, strike, vol, rate, expiry)
opt.TwoMoments(price, strike, vol, rate, expiry)

price = mktData['underlying'][0]

index = 1
strike = list(mktData['ticker'].str[-3:].astype(int))[index]
vol = mktData['imp vol'][index]
rate = mktData['int rate'][index]
expiry = (expiryDate - valueDate).days

optionPrice = mktData['option price'][index]

opt.TwoMomentsMode(price, strike, vol, rate, expiry)
optionPrice
#**************************************************************************************
#======================================================================================




























