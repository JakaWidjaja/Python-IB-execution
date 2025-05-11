import numpy as np
from scipy.optimize import minimize

from UDF.OptionPricer import MixLogNormal

class CalibrateMixLogNormal:
    def __init__(self):
        pass
    
    def Calibrate(self, marketPrice, strike, intRate, expiry, modelType, optionType):
        self.marketPrice = marketPrice #List of options market prices 
        self.strike      = strike      #List of strikes
        self.intRate     = intRate
        self.expiry      = expiry
        self.modelType   = modelType   #Black-Scholes or Black76
        self.optionType  = optionType
        
        #Initiate object
        model = MixLogNormal.MixLogNormal()

        def error(params, marketPrice, strike, intRate, expiry):
            w1, f1, f2, sigma1, sigma2 = params
            
            w1 = max(0, min(w1, 1)) #Ensure the weight is between 0 and 1

            modelPrice = [model.OptionPrice(k, rate, self.expiry, w1, f1, f2, sigma1, sigma2, self.modelType, self.optionType) for k, rate in 
                          zip(self.strike, self.intRate) ]
            
            return np.sum((np.array(self.marketPrice) - np.array(modelPrice))**2)


        init = [0.5, self.strike[len(self.strike)//2], self.strike[len(self.strike)//2], 0.38, 0.38]
        bnd = [(0, 1), (0.01, None), (0.01, None), (0.01, None), (0.01, None)]
        
        res = minimize(error, init, bounds = bnd, args = (self.marketPrice, self.strike, self.intRate, self.expiry), method = 'trust-constr')
        
        return res.x
    
if __name__ == '__main__':
    
    calib = CalibrateMixLogNormal()
    strike = [90, 95, 100, 105, 110]
    marketPrice = [12, 8, 5, 3, 1.5]
    rate = [0.03, 0.03, 0.03, 0.03, 0.03]
    expiry = 1
    
    xx = calib.Calibrate(marketPrice, strike, rate, expiry, 'Black-Scholes', 'call')
    w, F1, F2, sigma1, sigma2 = xx.x
    
    ml = MixLogNormal.MixLogNormal()
    model_prices = [ml.OptionPrice(k, 0.05, 1, w, F1, F2, sigma1, sigma2, 'Black-Scholes', 'call') for k in strike]


















