import numpy as np
from scipy.stats import norm

class OptionPrice:
    def __init__(self):
        pass
    
    def BlackScholes(self, stock, strike, vol, expiry, rate, optType):
        self.stock  = stock
        self.strike = strike
        self.vol    = vol
        self.expiry = expiry
        self.rate   = rate
        self.optType = optType
        
        discount = np.exp(-self.expiry * self.rate)
        
        d1 = (np.log(self.stock / self.strike) + self.expiry * (self.rate + 0.5 * (self.vol**2))) / \
                (self.vol * np.sqrt(self.expiry))
                
        d2 = d1 - self.vol * np.sqrt(self.expiry)
        
        if optType == 'Call' or 'call':
            optValue = self.stock * norm.cdf(d1) - self.strike * discount * norm.cdf(d2)
        elif optType == 'Put' or 'put':
            optValue = self.strike * discount * norm.cdf(-d2) - self.stock * norm(-d1)
            
        return optValue
    
    def Black76(self, forward, strike, vol, expiry, rate, optType):
        self.forward = forward
        self.strike  = strike
        self.vol     = vol
        self.expiry  = expiry
        self.rate    = rate
        self.optType = optType
        
        discount = np.exp(-self.expiry * self.rate)
        
        d1 = (np.log(self.forward / self.strike) + self.expiry * (self.rate + 0.5 * (self.vol**2))) / \
                (self.vol * np.sqrt(self.expiry))
                
        d2 = d1 - self.vol * np.sqrt(self.expiry)
        
        if optType == 'Call' or 'call':
            optValue = discount * (self.forward * norm.cdf(d1) - self.strike * norm.cdf(d2))
        elif optType == 'Put' or 'put':
            optValue = discount * (self.strike * norm.cdf(-d2) - self.forward * norm.cdf(-d1))
            
        return optValue
    
    def MixLogNormal(self, price1, price2, vol1, vol2, weight, strike, expiry, rate, callPut, optType):
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
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        