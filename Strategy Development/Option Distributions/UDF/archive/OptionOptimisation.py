from scipy.optimize import minimize
from UDF.OptionPrice import OptionPrice

import numpy as np

class OptionOptimisation:
    def __init__(self):
        self.optPrice = OptionPrice()
    
    def BSVolatility(self, marketPrice, stockPrice, strike, expiry, rate, optType):
        self.marketPrice = marketPrice 
        self.stockPrice  = stockPrice
        self.strike      = strike
        self.expiry      = expiry
        self.rate        = rate
        self.optType     = optType
        
        def ObjectiveFunc(sigma):
            modelPrice = self.optPrice.BlackScholes(self.stockPrice, self.strike, sigma, self.expiry,
                                                    self.rate, self.optType)
            
            return (modelPrice - self.marketPrice) ** 2
        
        try:
            guess = 0.5
            impliedVol = minimize(ObjectiveFunc, guess, bounds = [(1e-8, np.inf)], method='L-BFGS-B')
        except ValueError:
            return None
        
        return impliedVol.x[0]
    
    def Black76Volatility(self, marketPrice, stockPrice, strike, expiry, rate, optType):
        self.marketPrice = marketPrice 
        self.stockPrice  = stockPrice
        self.strike      = strike
        self.expiry      = expiry
        self.rate        = rate
        self.optType     = optType
        
        def ObjectiveFunc(sigma):
            modelPrice = self.optPrice.Black76(self.stockPrice, self.strike, sigma, self.expiry, self.rate,
                                               self.optType)
            
            return (modelPrice - self.marketPrice) ** 2
        
        try:
            guess = 0.5
            impliedVol = minimize(ObjectiveFunc, guess, bounds = [(1e-8, np.inf)], method='L-BFGS-B')
        except ValueError:
            return None
        
        return impliedVol.x[0]
    
    def MixLogPriceVolWeight(self, marketPrice, strike, expiry, rate, callPut, optType):
        self.marketPrice = marketPrice 
        self.strike      = strike
        self.expiry      = expiry
        self.rate        = rate
        self.callPut     = callPut
        self.optType     = optType
        
        def ObjectiveFunc(params):
            price1 = params[0]
            price2 = params[1]
            vol1   = params[2]
            vol2   = params[3]
            weight = params[4]
            
            modelPrice = self.optPrice.MixLogNormal(price1, price2, vol1, vol2, weight, self.strike, 
                                                    self.expiry, self.rate, self.callPut, self.optType)
            
            return (modelPrice - self.marketPrice) ** 2
        
        #try:
        guess = [20, 20, 0.05, 0.05, 0.8]
        bnd = [(1e-8, np.inf), (1e-8, np.inf), (1e-8, np.inf), (1e-8, np.inf), (0, 1)]
        parameters = minimize(ObjectiveFunc, guess, bounds = bnd, method='SLSQP')
        #except ValueError:
            #return None
        
        return parameters.x
            

if __name__ == '__main__':
    expiry = 20/365
    price = 20.66
    strike = 20
    rate = 0.0549
    flag = 'Call'
    marketPrice = 1.8
    
    optim = OptionOptimisation()
    
    impliedVol = optim.BSVolatility(marketPrice, price, strike, expiry, rate, flag)
    impliedVol
    
    impliedVol = optim.Black76Volatility(marketPrice, price, strike, expiry, rate, flag)
    
    impliedVol = optim.MixLogPriceVolWeight(marketPrice, strike, expiry, rate, flag, 'BlackScholes')
    impliedVol


    opt = OptionPrice()
    opt.MixLogNormal(impliedVol.x[0], impliedVol.x[1], impliedVol.x[2],
                     impliedVol.x[3], impliedVol.x[4], strike, expiry, rate, 'call', 'BlackScholes')
