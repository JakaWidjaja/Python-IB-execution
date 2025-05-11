#Set directory
import os
os.chdir('/home/lun/Desktop/Folder 2/Strategy Development/Using Option Price to Trade Underlying')
directory = os.getcwd()

from UDF.OptionPricer import Black76
from UDF.OptionPricer import BlackScholes
from UDF.ExpectedProfitLoss import ExpectedProfitLoss

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
bl = Black76.Black76()

valueDate  = optData['Value Date'][0]
expiryDate = optData['Expiry'][0]
underlyingPrice = optData['Underlying Price'][0]
expiry = (expiryDate - valueDate).days / 365.0

def objFunc(rate, optionData):
    error = 0.0
    for i in range(len(optionData)):
        marketPrice = optionData.iloc[i, optionData.columns.get_loc('Option Price')]
        strike      = optionData.iloc[i, optionData.columns.get_loc('Strike')]
        impVol      = optionData.iloc[i, optionData.columns.get_loc('Implied Vol')] / 100.0
        optType     = optionData.iloc[i, optionData.columns.get_loc('Type')]
        
        modelPrice = bl.Price(underlyingPrice, strike, impVol, expiry, rate, optType)
        error += ((marketPrice - modelPrice)) ** 2
    return error

bnd = [(0, 1)]
res = minimize(objFunc, x0 = [0.02], bounds = bnd, args = (optData), method = "trust-constr")
rate = res.x
rate = days60
    

totalVolume = sum(optData['Volume'])
calibData = []
#data: (strike price, market price, type, weight)
for i in range(len(optData)):
    strikePrice = optData.iloc[i, optData.columns.get_loc('Strike')]
    marketPrice = optData.iloc[i, optData.columns.get_loc('Model Price')]
    optionType  = optData.iloc[i, optData.columns.get_loc('Type')]
    weight      = optData.iloc[i, optData.columns.get_loc('Volume')] / totalVolume
    
    calibData.append((strikePrice, marketPrice, optionType, weight))
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
from UDF.ExpectedProfitLoss import ExpectedProfitLoss
el = ExpectedProfitLoss.ExpectedProfitLoss()
params = [el.Calibrate(underlyingPrice, calibData, expiry, rate)]

mu = params[0][0]
sigma = params[0][1]

i = 10
weight = [optData.iloc[i, optData.columns.get_loc('Volume')] / totalVolume]
el.ExpectedPL(underlyingPrice, expiry, rate, mu, sigma)
#**************************************************************************************
#======================================================================================
f = underlyingPrice * np.exp(rate * expiry)
f = 9500

el.CDF(underlyingPrice, f, expiry, mu, sigma)



























