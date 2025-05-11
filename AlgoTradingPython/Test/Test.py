#Set directory
import os
os.chdir('/home/lun/Desktop/Folder 2/AlgoTradingPython')

import pandas as pd
import numpy as np
import datetime as dt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt 
from scipy.special import gamma, digamma, gammaln, factorial, loggamma
from scipy.optimize import minimize

from itertools import combinations

from UDF.Portfolio                   import PortfolioSelection, PortfolioWeights
from UDF.Utilities                   import Autocovariance, ReScaleTimeSeries
from UDF.Models.OrnsteinUhlenbeck    import OrnsteinUhlenbeck 
from UDF.Models.BertramEntryExit     import BertramEntryExit
from Strategy.MeanRevertingPortfolio import MeanRevertingPortfolio

#Download Data
stockList = ['AMCR', 'BAC', 'BK', 'BKR', 'CNP', 'CSCO', 'D', 'DIS', 'INTC', 'IVZ', 'KHC',
             'LNT', 'MRO', 'PCG', 'PFE', 'T', 'VZ', 'XEL']

df = pd.read_csv('Test/Data/' + 'AMCR' + '.csv')
date = pd.to_datetime(df['DateTime'], format='%d/%m/%Y %H:%M:%S')
data = pd.DataFrame(date)

for name in stockList:
    temp = pd.read_csv('Test/Data/' + name + '.csv')
    temp['mid'] = (temp['Ask'] + temp['Bid']) / 2.0
    
    data[name] = temp['mid']
    

portSelect = PortfolioSelection.PortfolioSelection()
stocks = portSelect.PCA(data,3000, 6)

#Combinations of stocks
combStocks = list(combinations(stocks, 5))

weights = {}
w = PortfolioWeights.PortfolioWeights()
oh = OrnsteinUhlenbeck.OrnsteinUhlenbeck()


signal = MeanRevertingPortfolio.MeanRevertingPortfolio(4, 3000)

for c in combStocks:
    stockList = data.loc[:, c].tail(3000)
    stockList = data.loc[:, c][10800 : 13801]
    #calculate 1 day return 
    
    weights[c] = w.BoxTiao(stockList, 1, [0.5, 0.5, 0.5, 0.5, 0.5], 'longshort', 3000)
    
    multiply = stockList * weights[c]
    portfolioTimeSeries = multiply.sum(axis = 1)
    
    #Normalised
    a = (portfolioTimeSeries - min(portfolioTimeSeries)) / (max(portfolioTimeSeries) - min(portfolioTimeSeries))    
    mu, theta, sigma = oh.Moment(a)
    
numTopStocks = 8
stockCombs = signal.StockSelection(data, numTopStocks)
    
l, s = signal.EntryExitSignal(stockCombs, data, 'longshort')

longTracking = []
shortTracking = []
import warnings
warnings.filterwarnings("ignore")
for i in range(3000, len(data)):
    timeSeries = data[:i]
    long, short = signal.EntryExitSignal(stockCombs, timeSeries ,'longshort')
    if long:
        print(long, i) #i = 3545
        break
    longTracking.append(long)
    shortTracking.append(short)

s1 = timeSeries.iloc[3544, timeSeries.columns.get_loc('T')] * 0.48398783
s2 = timeSeries.iloc[3544, timeSeries.columns.get_loc('D')] * -0.38736927
s3 = timeSeries.iloc[3544, timeSeries.columns.get_loc('MRO')] * 0.61757951
s4 = timeSeries.iloc[3544, timeSeries.columns.get_loc('KHC')] * 0.27580192

s1 + s2 + s3 + s4

#Create portfolio value
plt.plot(a)
plt.plot(portfolioTimeSeries)

c = combStocks[3]
port = data.loc[:, c]

entryExit = BertramEntryExit.BertramEntryExit()

priceList = []
entList = []
extList = []
signal = []
for i in range(len(data) - 3000):
    portTimeSeries = port[i : i + 3000]

    weights[c] = w.BoxTiao(portTimeSeries, 1, [0.5, 0.5, 0.5, 0.5, 0.5], 'longshort', 3000)
    
    multiply = portTimeSeries * weights[c]
    portfolioTimeSeries = multiply.sum(axis = 1)
    
    #norm = list((portfolioTimeSeries - min(portfolioTimeSeries)) / (max(portfolioTimeSeries) - min(portfolioTimeSeries))) 
    norm = list(2*(portfolioTimeSeries - min(portfolioTimeSeries)) / (max(portfolioTimeSeries) - min(portfolioTimeSeries))-1) 
    #norm = list((portfolioTimeSeries - np.average(portfolioTimeSeries)) /np.std(portfolioTimeSeries))
    mu, theta, sigma = oh.Moment(norm)
    
    ent, ext = entryExit.CalibrateModel(0.005, max(norm), min(norm), mu, theta, sigma)
    
    if norm[-2] < ext and norm[-3] < ext and norm[-1] > ext:
        signal.append(i)

    priceList.append(norm[-1])
    entList.append(ent)
    extList.append(ext)
    
    if i == 300:
        break



signal.EntryExitSignal(stockCombs, data[0:3000])

start = 0
end = -1
plt.plot(priceList[start:end])

plt.plot(extList[start:end])
plt.plot(entList[start:end])

plt.plot(norm)


plt.plot(portfolioTimeSeries)
norm = (portfolioTimeSeries - np.average(portfolioTimeSeries)) /np.std(portfolioTimeSeries)

aaa = 7.455e-01
np.sqrt((sigma**2) / (2.0 * theta)) * aaa + mu
np.sqrt((sigma**2) / (2.0 * theta)) * aaa - mu

np.sqrt((2 * theta) / (sigma**2)) * (aaa - mu)
np.sqrt((2 * theta) / (sigma**2)) * (aaa + mu)


def w1(z, tolerance = 1e-8):
    total1 = 0.0
    total2 = 0.0
    i = 1

    sqrt2z = np.sqrt(2) * z
    while True:
        term1 = (((sqrt2z ) ** i) / factorial(i + 1)) * gamma(i / 2)
        term2 = (((sqrt2z  * -1) ** i) / factorial(i + 1)) * gamma(i / 2)

        if abs(term1 - term2) < tolerance:
            break
        total1 += term1
        total2 += term2
        i += 1
    
    total1 = (total1 * 0.5) ** 2
    total2 = (total2 * 0.5) ** 2
    
    return total1 - total2
'''
def w2(z, tolerance = 1e-8):
    # Set numpy to raise errors on overflow
    old_settings = np.seterr(over='raise')
    
    total = 0.0
    i = 1

    sqrt2z = np.sqrt(2) * z
    while True:
        const = 2 * i - 1
        try:
            term = (((sqrt2z) ** const) / factorial(const)) * gamma(i - 0.5) * digamma(i - 0.5)
        except FloatingPointError:
            break

        if abs(term) < tolerance:
            break

        total += term
        i += 1
    np.seterr(**old_settings)
    return total
'''
def w2(z, tolerance = 1e-8):
    # Set numpy to raise errors on overflow
    old_settings = np.seterr(over='raise')
    
    total = 0.0
    i = 1

    sqrt2z = np.sqrt(2) * z
    while True:
        const = 2 * i - 1

        term = (((sqrt2z) ** const) / factorial(const)) * gamma(i - 0.5) * digamma(i - 0.5)

        if abs(term) < tolerance:
            break

        total += term
        i += 1
    np.seterr(**old_settings)
    return total
        
        
def VarT(entryPrice, exitPrice):

    return w1(entryPrice) - w1(exitPrice) - w2(entryPrice) + w2(exitPrice)
'''
def ET(entryPrice, exitPrice, tolerance = 1e-8):
    sqrt2 = np.sqrt(2)
    total = 0.0
    k = 1
    # Set numpy to raise errors on overflow
    old_settings = np.seterr(over='raise')
    
    while True:
        const = 2 * k - 1
        try:
            term = ((sqrt2 * entryPrice) ** const - (sqrt2 * exitPrice) ** const) / factorial(const + 1) * gamma(const / 2.0)
        except FloatingPointError:
            break
        
        if abs(term) < tolerance:
            break
        total += term
        k += 1

    return total
'''
def ET(entryPrice, exitPrice, tolerance = 1e-8):
    sqrt2 = np.sqrt(2)
    total = 0.0
    k = 1
    print(entryPrice, exitPrice)
    while True:
        const = 2 * k - 1
        #print(entryPrice, exitPrice, 
              #((sqrt2 * entryPrice) ** const - (sqrt2 * exitPrice) ** const) / factorial(const + 1) * gamma(const / 2.0))
        term = ((sqrt2 * entryPrice) ** const - (sqrt2 * exitPrice) ** const) / factorial(const + 1) * gamma(const / 2.0)
                
        if abs(term) < tolerance:
            break
        total += term
        k += 1

    return total


def ZM(entryPrice, exitPrice, costPrice, mu, theta, sigma):
    #if ET(entryPrice, exitPrice) == 0:
        #ZMAdjust = np.sqrt(2 / (theta * sigma * sigma)) * (exitPrice - entryPrice - costPrice)
    #else:
    ZMAdjust = np.sqrt(2 / (theta * sigma * sigma)) * (exitPrice - entryPrice - costPrice) / ET(entryPrice, exitPrice)
    return ZMAdjust

def ZV(entryPrice, exitPrice, costPrice, sigma):
    # Set numpy to raise errors on overflow
    #old_settings = np.seterr(over='raise')
    
    pi = exitPrice - entryPrice - costPrice
    denom = ET(entryPrice, exitPrice)
    #if denom == 0:
        #denom = 1
        
    #try:
    ZVAdjust = (2/(sigma**2)) * ((pi ** 2) / (denom ** 3)) * VarT(entryPrice, exitPrice)
    #except FloatingPointError:
        #ZVAdjust = (2/(sigma**2)) * (pi ** 2) * VarT(entryPrice, exitPrice)                           
        
    return ZVAdjust

# Define the combined objective function to maximize ZM
def objective(x, costPrice, mu, theta, sigma):
    entryPrice = x[0]
    exitPrice = x[1]
    
    entryPriceAdjust = np.sqrt(2 * theta / (sigma**2)) * (entryPrice - mu)
    exitPriceAdjust = np.sqrt(2 * theta / (sigma**2)) * (exitPrice - mu)

    return -ZM(entryPriceAdjust, exitPriceAdjust, costPrice, mu, theta, sigma) * 1e5  # Negate to maximize

# Constraints
def constraint1(x, costPrice, eta, mu, theta, sigma):
    entryPrice = x[0]
    exitPrice = x[1]
    
    entryPriceAdjust = np.sqrt(2 * theta / (sigma**2)) * (entryPrice - mu)
    exitPriceAdjust = np.sqrt(2 * theta / (sigma**2)) * (exitPrice - mu)
    return eta - ZV(entryPriceAdjust, exitPriceAdjust, costPrice, sigma)  # ZV < eta

def constraint2(x, mu, theta, sigma):
    entryPrice = x[0]
    exitPrice = x[1]
    
    entryPriceAdjust = np.sqrt(2 * theta / (sigma**2)) * (entryPrice - mu)
    exitPriceAdjust = np.sqrt(2 * theta / (sigma**2)) * (exitPrice - mu)
    return entryPriceAdjust - exitPriceAdjust # exitPrice < entryPrice

def constraint3(x, mu, theta, sigma):
    entryPrice = x[1]
    entryPriceAdjust = np.sqrt(2 * theta / (sigma**2)) * (entryPrice - mu)
    return entryPriceAdjust  # entryPrice > 0

# Set the parameters for the problem
costPrice = 0.0005  # Example value, set this accordingly
eta = sigma  # Example value for eta

# Initial guess
x0 = np.array([mu, mu])
x0 = np.array([0.5, 0.5]) 
x0 = np.array([max(norm), min(norm)])  # Example initial guess
x0 = np.array([-10, 10])

# Define the constraints in the form required by scipy.optimize.minimize
cons = [{'type': 'ineq', 'fun': constraint1, 'args': (costPrice, eta, mu, theta, sigma)},
        {'type': 'ineq', 'fun': constraint2, 'args': (mu, theta, sigma)},
        {'type': 'ineq', 'fun': constraint3, 'args': (mu, theta, sigma)}]

# Define bounds for the optimization variables (entryPrice and exitPrice)
bnd = [(0, 1), (0, 1)]

# Perform the minimization
result = minimize(objective, x0, method = 'SLSQP', args=(costPrice, mu, theta, sigma), constraints=cons, bounds= bnd)
result

result.x[0]
result.x[1]



np.sqrt((sigma * sigma) / (2 * theta)) * result.x[1] + mu
np.sqrt((sigma * sigma) / (2 * theta)) * result.x[0] + mu


np.sqrt((2 * theta) / (sigma**2)) * (result.x[0] - mu)
np.sqrt((2 * theta) / (sigma**2)) * (result.x[1] + mu)


plt.plot(a)

mu - sigma/theta
