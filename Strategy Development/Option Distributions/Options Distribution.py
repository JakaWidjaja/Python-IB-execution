#Set directory
import os
os.chdir('/home/lun/Desktop/Folder 2/Strategy Development/Option Distributions')
directory = os.getcwd()

import numpy as np
import pandas as pd
import datetime as dt
from scipy.optimize import minimize

from UDF.OptionPricer import BlackScholes
from UDF.RiskNeutralDensity import CalibrateBeta
from UDF.RiskNeutralDensity import CalibrateMixLogNormal
from UDF.OptionPricer import CRRA
from UDF.RealWorldDensity import CRRAUtility

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
bl = BlackScholes.BlackScholes()

valueDate = dt.datetime(2024, 10, 10).date()
expiryDate = dt.datetime(2024, 11, 15).date()

mktData['int rate'] = 0.0

def objFunc(rate):
    
    modelPrice = bl.Price(undPrice, strike, impVol, expiry, rate, "call")
    
    error = ((optPrice - modelPrice) * 100) ** 2
    
    return error

for i in range(len(mktData)):
    tickerName = mktData.iloc[i, mktData.columns.get_loc('ticker')]
    undPrice = mktData.loc[mktData['ticker'] == tickerName, 'underlying'].values[0]
    optPrice = mktData.loc[mktData['ticker'] == tickerName, 'option price'].values[0]
    strike = int(tickerName[-3:])
    impVol = mktData.loc[mktData['ticker'] == tickerName, 'imp vol'].values[0]
    expiry = (expiryDate - valueDate).days /360
    
    res = minimize(objFunc, [0.005])
    
    mktData.iloc[i, mktData.columns.get_loc('int rate')] = res.x[0]
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
#Calibrate Beta and Mix Log-Normal model
betaCalibrate = CalibrateBeta.CalibrateBeta()
mlnCalibrate  = CalibrateMixLogNormal.CalibrateMixLogNormal()

marketPrices = list(mktData['option price'])
strikes      = list(mktData['ticker'].str[-3:].astype(int))
intRate      = list(mktData['int rate'])
expiry = (expiryDate - valueDate).days / 365.0

betaParams = betaCalibrate.Calibrate(marketPrices, strikes, intRate, expiry)
mlnParams = mlnCalibrate.Calibrate(marketPrices, strikes, intRate, expiry, 'black-scholes', 'call')

from UDF.RealWorldDensity import CRRAUtility
from UDF.RiskNeutralDensity import BetaDensity, MixLogNormalDensity

strike = 240
rate = intRate[-2]

crraDensity = CRRAUtility.CRRAUtility()
betaDensity = BetaDensity.BetaDensity()
mlnDensity  = MixLogNormalDensity.MixLogNormalDensity()

def errorBeta(ra):
    
    densityNeutral = betaDensity.PDF(strike, betaParams[0], betaParams[1], betaParams[2], betaParams[3])  
    densityReal = crraDensity.BetaPDF(strike, ra, betaParams[0], betaParams[1], betaParams[2], betaParams[3])
    
    return ((densityNeutral - densityReal)*100000) ** 2

guess = [2.5]
bnd = [(0, None)]
raBeta = minimize(errorBeta, x0 = guess, bounds = bnd, method = 'Nelder-Mead')

#crraDensity.BetaPDF(strike, raBeta.x[0], betaParams[0], betaParams[1], betaParams[2], betaParams[3])
#betaDensity.PDF(strike, betaParams[0], betaParams[1], betaParams[2], betaParams[3]) 


def errormln(ra):
    
    densityNeutral = mlnDensity.PDF(strike, mlnParams[0], mlnParams[1], mlnParams[2], mlnParams[3], mlnParams[4], expiry)  
    densityReal = crraDensity.BetaPDF(strike, ra, betaParams[0], betaParams[1], betaParams[2], betaParams[3])
    
    return ((densityNeutral - densityReal)*100000) ** 2

guess = [50.5]
bnd = [(0, None)]
raMLN = minimize(errormln, x0 = guess, bounds = bnd, method = 'Nelder-Mead')
minimize(errormln, x0 = guess, bounds = bnd, method = 'trust-constr')

crraDensity.BetaVol(raBeta.x[0], betaParams[0], betaParams[1], betaParams[2], betaParams[3])
crraDensity.MixLogNormalVol(raMLN.x[0], mlnParams[0], mlnParams[1], mlnParams[2], mlnParams[3], mlnParams[4], expiry)

#Calculate option Price
from UDF.OptionPricer import CRRA
realOption = CRRA.CRRA()


strike = 225
rate = intRate[0]
mkt = marketPrices[0]
riskAversion = 47.788

realOption.MixLogNormalOptionPrice(strike, rate, expiry, 'call', riskAversion, mlnParams[0], mlnParams[1], mlnParams[2], mlnParams[3], mlnParams[4])

realOption.BetaOptionPrice(strike, rate, expiry, 'call', riskAversion, betaParams[0], betaParams[1], betaParams[2], betaParams[3])

def error(risk, s, r, e, a, b, p, q, mkt):
    
    opt = realOption.BetaOptionPrice(s, r, e, 'call', risk, a, b, p, q)
    print(opt, (opt - mkt)**2)
    return ((opt - mkt)*1000000)**2

guess = [47.788]
bnd = [(None,None)]

minimize(error, x0 = guess, bounds = bnd, args = (strike, rate, expiry, betaParams[0], betaParams[1], betaParams[2], betaParams[3],mkt), 
         method = 'Nelder-Mead', options={
        'disp': True,   # Display convergence messages
        'gtol': 1e-6,   # Gradient norm tolerance for termination
    })
    
    
def error(risk, s, r, e, a0, a1, a2, a3, a4, mkt):
    
    opt = realOption.MixLogNormalOptionPrice(s, r, e, 'call', risk, a0, a1, a2, a3, a4)
    print(opt, ((opt - mkt))**2)
    return ((opt - mkt))**2

guess = [100.1]
bnd = [(None,None)]
a0 = mlnParams[0]
a1 = mlnParams[1]
a2 = mlnParams[2]
a3 = mlnParams[3]
a4 = mlnParams[4]
minimize(error, x0 = guess, bounds = bnd, args = (strike, rate, expiry, a0,a1,a2,a3,a4,mkt), method = 'trust-constr')
#**************************************************************************************
#======================================================================================

















