#Set directory
import os
os.chdir('/home/lun/Desktop/Folder 2/Strategy Development/Option Distributions')
directory = os.getcwd()

import scipy.special as sc
from scipy.optimize import minimize, differential_evolution
from scipy.integrate import quad
from scipy.special import beta
import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt

from UDF.BetaDistribution import BetaDistribution
from UDF.Black76          import Black76
from UDF.BlackScholes     import BlackScholes
from UDF.MixLogNormal     import MixLogNormal

#======================================================================================
#**************************************************************************************
#import data

#1-Day tick option
tickData = pd.read_csv(directory + '/data/AAPL.csv')
tickData225 = pd.read_csv(directory + '/data/AAPL225.csv')
tickData230 = pd.read_csv(directory + '/data/AAPL230.csv')
tickData235 = pd.read_csv(directory + '/data/AAPL235.csv')
tickData240 = pd.read_csv(directory + '/data/AAPL240.csv')
tickData245 = pd.read_csv(directory + '/data/AAPL245.csv')

mktData = pd.read_csv(directory + '/data/aaplMkt.csv')

tickData225['date just'] = pd.to_datetime(tickData225['date'], format = '%Y%m%d %H:%M:%S').dt.date
tickData230['date just'] = pd.to_datetime(tickData230['date'], format = '%Y%m%d %H:%M:%S').dt.date
tickData235['date just'] = pd.to_datetime(tickData235['date'], format = '%Y%m%d %H:%M:%S').dt.date
tickData240['date just'] = pd.to_datetime(tickData240['date'], format = '%Y%m%d %H:%M:%S').dt.date
tickData245['date just'] = pd.to_datetime(tickData245['date'], format = '%Y%m%d %H:%M:%S').dt.date

tickData['date just'] = pd.to_datetime(tickData['date'], format = '%Y%m%d %H:%M:%S').dt.date
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
#Get Int Rate
bl = BlackScholes()

tickerName = 'AAPL20241115C230'
valueDate = dt.datetime(2024, 10, 10).date()
expiryDate = dt.datetime(2024, 11, 15).date()

undPrice = mktData.loc[mktData['ticker'] == tickerName, 'underlying'].values[0]
optPrice = mktData.loc[mktData['ticker'] == tickerName, 'option price'].values[0]
strike = int(tickerName[-3:])
impVol = mktData.loc[mktData['ticker'] == tickerName, 'imp vol'].values[0]
expiry = (expiryDate - valueDate).days /360

def objFunc(rate):
    
    modelPrice = bl.Price(undPrice, strike, impVol, expiry, rate, "call")
    
    error = ((optPrice - modelPrice) * 100) ** 2
    
    return error

res = minimize(objFunc, [0.005])
res

bl.Price(undPrice, strike, impVol, expiry, res.x[0], "call")
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
#Extract Data
valueDate = dt.datetime(2024, 10, 10).date()
intRate = res.x[0]

optPrice225 = list(tickData225.loc[tickData225['date just'] == valueDate, 'close'])
optPrice230 = list(tickData225.loc[tickData225['date just'] == valueDate, 'close'])
optPrice235 = list(tickData225.loc[tickData225['date just'] == valueDate, 'close'])
optPrice240 = list(tickData225.loc[tickData225['date just'] == valueDate, 'close'])
optPrice245 = list(tickData225.loc[tickData225['date just'] == valueDate, 'close'])

price    = list(tickData.loc[tickData['date just'] == valueDate, 'close'])

strike225 = 225
strike230 = 230
strike235 = 235
strike240 = 240
strike245 = 245

impliedVol = []

for i, op in enumerate(optPrice225):
    iv225 = bl.ImpliedVol(optPrice225[i], price[i], strike225, expiry, intRate, 'call')
    iv230 = bl.ImpliedVol(optPrice230[i], price[i], strike230, expiry, intRate, 'call')
    iv235 = bl.ImpliedVol(optPrice235[i], price[i], strike235, expiry, intRate, 'call')
    iv240 = bl.ImpliedVol(optPrice240[i], price[i], strike240, expiry, intRate, 'call')
    iv245 = bl.ImpliedVol(optPrice245[i], price[i], strike245, expiry, intRate, 'call')
    
    impliedVol.append([iv225, iv230, iv235, iv240, iv245])
    
plt.plot(impliedVol)

bl.Price(undPrice, strike, 0.25, expiry, res.x[0], "call")
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
betaOption = BetaDistribution()

betaIV = []
for i, op in enumerate(optPrice):
    a, b, p, q = betaOption.calibrate(price[i], strike225, expiry, intRate, 'call', optPrice225[i])
    iv225 = betaOption.Moment(2, a, b, p, q)
    
    a, b, p, q = betaOption.calibrate(price[i], strike230, expiry, intRate, 'call', optPrice230[i])
    iv230 = betaOption.Moment(2, a, b, p, q)
    
    betaIV.append(betaImpliedVol)
    
plt.plot(betaIV)
#**************************************************************************************
#======================================================================================

























