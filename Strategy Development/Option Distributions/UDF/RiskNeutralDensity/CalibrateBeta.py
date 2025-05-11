
from UDF.OptionPricer import Beta

from scipy.optimize import minimize

class CalibrateBeta:
    def __init__(self):
        pass
    
    def Calibrate(self, marketPrice, strikes, intRate, expiry):
        self.marketPrice = marketPrice
        self.strikes     = strikes
        self.intRate     = intRate
        self.expiry      = expiry
        
        optionPricer = Beta.Beta()
        
        def error(params):
            a, b, p, q = params
            
            diff = [(optionPricer.OptionPrice(k, rate, self.expiry, a, b, p, q) - mktPrice)**2 for k, mktPrice, rate in 
                                                                            zip(self.strikes, self.marketPrice, self.intRate)]
            
            return sum(diff)
        
        init = [2, self.strikes[len(self.strikes) // 2], 2, 2]
        bnd = [(0.01, 10.0), (self.strikes[0] * 0.5, self.strikes[0] * 1.5), (0.01, 10.0), (0.01, 10.0)]
        
        res = minimize(error, x0 = init, bounds = bnd, method = 'trust-constr')
        
        return res.x
    
if __name__ == '__main__':
    
    b = CalibrateBeta()
    
    marketPrice = [10, 8, 6, 4, 2] 
    strikes = [90, 100, 110, 120, 130] 
    intRate = [0.03, 0.03, 0.03, 0.03, 0.03]
    expiry = 1.0
    
    b.Calibrate(marketPrice, strikes, intRate, expiry)
    
    