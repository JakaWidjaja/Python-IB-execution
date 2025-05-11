import numpy        as np
from scipy.stats    import norm
from scipy.optimize import minimize

class Black76:
    def __init__(self):
        pass
    
    def Price(self, forward, strike, vol, expiry, rate, optType):
        self.forward = forward
        self.strike  = strike
        self.vol     = vol
        self.expiry  = expiry
        self.rate    = rate
        self.optType = optType
        
        discount = np.exp(-self.expiry * self.rate)
        
        d1 = (np.log(self.forward / self.strike) + self.expiry * (0.5 * (self.vol**2))) / \
                (self.vol * np.sqrt(self.expiry))
                
        d2 = d1 - self.vol * np.sqrt(self.expiry)
        
        if optType.lower() == 'call':
            optValue = discount * (self.forward * norm.cdf(d1) - self.strike * norm.cdf(d2))
        elif optType.lower() == 'put':
            optValue = discount * (self.strike * norm.cdf(-d2) - self.forward * norm.cdf(-d1))
            
        return optValue
    
    def ImpliedVol(self, marketPrice, stockPrice, strike, expiry, rate, optType):
        self.marketPrice = marketPrice 
        self.stockPrice  = stockPrice
        self.strike      = strike
        self.expiry      = expiry
        self.rate        = rate
        self.optType     = optType
        
        def ObjectiveFunc(sigma):
            modelPrice = self.Price(self.stockPrice, self.strike, sigma, self.expiry, self.rate,
                                               self.optType)
            
            return (modelPrice - self.marketPrice) ** 2
        
        try:
            guess = 0.5
            impliedVol = minimize(ObjectiveFunc, guess, bounds = [(1e-8, np.inf)], method='L-BFGS-B')
        except ValueError:
            return None
        
        return impliedVol.x[0]