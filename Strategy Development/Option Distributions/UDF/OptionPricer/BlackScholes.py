import numpy        as np
from scipy.stats    import norm
from scipy.optimize import minimize

class BlackScholes:
    def __init__(self):
        pass
    
    def Price(self, stock, strike, vol, expiry, rate, optType):
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
        
        if self.optType.lower() == 'call':
            optValue = self.stock * norm.cdf(d1) - self.strike * discount * norm.cdf(d2)
        elif self.optType.lower() == 'put':
            optValue = self.strike * discount * norm.cdf(-d2) - self.stock * norm(-d1)
            
        return optValue
    
    def ImpliedVol(self, marketPrice, stockPrice, strike, expiry, rate, optType):
        self.marketPrice = marketPrice 
        self.stockPrice  = stockPrice
        self.strike      = strike
        self.expiry      = expiry
        self.rate        = rate
        self.optType     = optType
        
        def ObjectiveFunc(sigma):
            modelPrice = self.Price(self.stockPrice, self.strike, sigma, self.expiry,
                                                    self.rate, self.optType)
            
            return (modelPrice - self.marketPrice) ** 2
        
        try:
            guess = 0.25
            impliedVol = minimize(ObjectiveFunc, guess, bounds = [(1e-8, np.inf)], method='SLSQP')
        except ValueError:
            return None
        
        return impliedVol.x[0]