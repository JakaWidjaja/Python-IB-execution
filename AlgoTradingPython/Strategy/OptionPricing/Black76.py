import numpy        as np
from scipy.stats    import norm
from scipy.optimize import minimize

class Black76:
    def __init__(self):
        pass
    
    def D1D2(self, forward, strike, vol, expiry):
        d1 = (np.log(forward / strike) + expiry * (0.5 * (vol**2))) / (vol * np.sqrt(expiry))
        d2 = d1 - vol * np.sqrt(expiry)
        
        return d1, d2
    
    def Price(self, forward, strike, vol, expiry, rate, optType):        
        discount = np.exp(-expiry * rate)
        
        d1, d2 = self.D1D2(forward, strike, vol, expiry)
        
        if optType.lower() == 'call':
            optValue = discount * (forward * norm.cdf(d1) - strike * norm.cdf(d2))
        elif optType.lower() == 'put':
            optValue = discount * (strike * norm.cdf(-d2) - forward * norm.cdf(-d1))
            
        return optValue
    
    def ImpliedVol(self, marketPrice, stockPrice, strike, expiry, rate, optType):        
        def ObjectiveFunc(sigma):
            modelPrice = self.Price(stockPrice, strike, sigma, expiry, rate, optType)
            
            return (modelPrice - marketPrice) ** 2
        
        try:
            guess = 0.5
            impliedVol = minimize(ObjectiveFunc, guess, bounds = [(1e-8, np.inf)], method='Nelder-Mead')
        except ValueError:
            return None
        
        return impliedVol.x[0]
    
    def Delta(self, forward, strike, vol, expiry, rate, optType):
        discount = np.exp(- expiry * rate)
        
        d1, _ = self.D1D2(forward, strike, vol, expiry)
        
        if optType.lower() == 'call':
            return discount * norm.cdf(d1)
        elif optType.lower() == 'put':
            return discount * (norm.cdf(d1) - 1.0)
        else:
            raise ValueError('option type has to be "call" or "put"')
            
    def Gamma(self, forward, strike, vol, expiry, rate):
        discount = np.exp(-expiry * rate)
        
        d1, _ = self.D1D2(forward, strike, vol, expiry)
        
        return discount * norm.pdf(d1) / (forward * vol * np.sqrt(expiry))
    
    def Vega(self, forward, strike, vol, expiry, rate):
        discount = np.exp(- expiry * rate)
        
        d1, _ = self.D1D2(forward, strike, vol, expiry)
        
        return discount * forward * norm.pdf(d1) * np.sqrt(expiry)
        
        
        
if __name__ == '__main__':
    optionPrice = [131.25, 137.15, 143.4, 149.9, 156.9, 164.25, 172.0, 180.25, 189.0, 198.15, 186.65, 172.0,\
                   158.0, 144.75, 132.25, 120.25]
    undPrice = 6853.75
    strikes = [6625.0, 6650.0, 6675.0, 6700.0, 6725.0, 6750.0, 6775.0, 6800.0, 6825.0, 6850.0, 6875.0, 6900.0,\
               6925.0, 6950.0, 6975.0, 7000.0]
    expiry = 0.09166666666666666
    intRate = 0.03709792287830557
    optType = ['put', 'put', 'put', 'put', 'put', 'put', 'put', 'put', 'put', 'put', 'call', 'call', 'call',\
               'call', 'call', 'call']
    
    index = 1
    
    bl76 = Black76()
    
    bl76.ImpliedVol(optionPrice[index], undPrice, strikes[index], expiry, intRate, optType[index])
    
    bl76.Price(undPrice, strikes[index], 0.2759765624999998, expiry, intRate, optType[index])        


 
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        