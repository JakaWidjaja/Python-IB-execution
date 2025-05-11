import numpy        as np
from scipy.optimize import minimize

class MixLogNormal:
    def __init__(self):
        pass
    
    def Price(self, price1, price2, vol1, vol2, weight, strike, expiry, rate, callPut, optType):
        self.price1  = price1
        self.price2  = price2
        self.vol1    = vol1
        self.vol2    = vol2
        self.weight  = weight
        self.strike  = strike
        self.expiry  = expiry
        self.rate    = rate
        self.callPut = callPut
        self.optType = optType
        
        weight1 = self.weight
        weight2 = 1 - self.weight
        
        if optType == 'BlackScholes':
            optPrice1 = self.BlackScholes(self.price1, self.strike, self.vol1, self.expiry, self.rate, self.callPut)
            optPrice2 = self.BlackScholes(self.price2, self.strike, self.vol2, self.expiry, self.rate, self.callPut)
        
        elif optType == 'Black76':
            optPrice1 = self.Black76(self.price1, self.strike, self.vol1, self.expiry, self.rate, self.callPut)
            optPrice2 = self.Black76(self.price2, self.strike, self.vol2, self.expiry, self.rate, self.callPut)
        else:
            raise ValueError("Option type error")
            
        optPrice = weight1 * optPrice1 + weight2 * optPrice2
        
        return optPrice
    
    def ParamCalib(self, marketPrice, strike, expiry, rate, callPut, optType):
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