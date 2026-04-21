import sys
sys.path.append("/home/lun/Desktop/Folder 2/Python_Model/OptionPricing")

import numpy        as np
from scipy.optimize import minimize
from scipy.stats    import norm

import Black76      as bl76
import BlackScholes as bs

class MixLogNormal:
    def __init__(self):
        pass
    
    def F2(self, price, w1, f1):
        return (price - (w1 * f1)) / (1 - w1)
    
    def OptionPrice(self, underlyingPrice, strike, intRate, expiry, w1, f1, sigma1, sigma2, modelType, optionType):
        # Initiale the model
        if modelType == 'Black76':
            model = bl76.Black76()
        elif modelType == 'BlackScholes' or 'Black-Scholes':
            model = bs.BlackScholes()
            
        # F2
        f2 = self.F2(underlyingPrice, w1, f1)
        
        price1 = model.Price(f1, strike, sigma1, expiry, intRate, optionType)
        price2 = model.Price(f2, strike, sigma2, expiry, intRate, optionType)

        return w1 * price1 + (1 - w1) * price2
    
    def Calibrate(self, underlyingPrice, marketPrice, strike, intRate, expiry, modelType, optionType):        
        def error(params, marketPrice, strike, intRate, expiry):
            w1, f1, sigma1, sigma2 = params
            
            w1 = max(0, min(w1, 1)) #Ensure the weight is between 0 and 1

            modelPrice = [self.OptionPrice(underlyingPrice, k, rate, expiry, w1, f1, sigma1, sigma2, modelType, optionType) for k, rate in 
                          zip(strike, intRate) ]
            
            return np.sum((np.array(marketPrice) - np.array(modelPrice))**2)


        init = [0.5, strike[len(strike)//2], 0.38, 0.38]
        bnd = [(0, 1), (0.01, None), (0.01, None), (0.01, None)]
        
        res = minimize(error, init, bounds = bnd, args = (marketPrice, strike, intRate, expiry), method = 'trust-constr')
        print(res)
        return list(res.x)
    
    def PDF(self, price, w1, f1, sigma1, sigma2, expiry):        
        f2 = self.F2(price, w1, f1)
        
        ln1 = norm.pdf(np.log(price), loc = np.log(f1) - 0.5 * sigma1**2 * expiry, scale = sigma1 * np.sqrt(expiry)) / price
        ln2 = norm.pdf(np.log(price), loc = np.log(f2) - 0.5 * sigma2**2 * expiry, scale = sigma2 * np.sqrt(expiry)) / price
        
        return w1 * ln1 + (1 - w1) * ln2
    
    def CDF(self, price, w1, f1, sigma1, sigma2, expiry):
        f2 = self.F2(price, w1, f1)
        
        ln1 = norm.cdf(np.log(price), loc = np.log(f1) - 0.5 * sigma1**2 * expiry, scale = sigma1 * np.sqrt(expiry))
        ln2 = norm.cdf(np.log(price), loc = np.log(f2) - 0.5 * sigma2**2 * expiry, scale = sigma2 * np.sqrt(expiry))
        
        return w1 * ln1 + (1 - w1) * ln2
    
    def Moment(self, momentNum, price, w1, f1, sigma1, sigma2, expiry):
        f2 = self.F2(price, w1, f1)
        
        e1 = (f1**momentNum) * np.exp(0.5 * momentNum * (momentNum - 1) * (sigma1**2) * expiry)
        e2 = (f2**momentNum) * np.exp(0.5 * momentNum * (momentNum - 1) * (sigma2**2) * expiry)
        
        return w1 * e1 + (1.0 - w1) * e2
    
    def FirstMoment(self, price, w1, f1, sigma1, sigma2, expiry):
        return self.Moment(1, price, w1, f1, sigma1, sigma2, expiry)
    
    def SecondMoment(self, price, w1, f1, sigma1, sigma2, expiry):
        return self.Moment(2, price, w1, f1, sigma1, sigma2, expiry)
    
    def ThirdMoment(self, price, w1, f1, sigma1, sigma2, expiry):
        return self.Moment(3, price, w1, f1, sigma1, sigma2, expiry)
    
    def Mean(self, price, w1, f1, sigma1, sigma2, expiry):
        return self.FirstMoment(price, w1, f1, sigma1, sigma2, expiry)
    
    def Variance(self, price, w1, f1, sigma1, sigma2, expiry):
        u1 = self.FirstMoment(price, w1, f1, sigma1, sigma2, expiry)
        u2 =self.SecondMoment(price, w1, f1, sigma1, sigma2, expiry)
        
        return u2 - u1**2
    
    def Skewness(self, price, w1, f1, sigma1, sigma2, expiry):
        u1 = self.FirstMoment(price, w1, f1, sigma1, sigma2, expiry)
        u2 = self.SecondMoment(price, w1, f1, sigma1, sigma2, expiry)
        u3 = self.ThirdMoment(price, w1, f1, sigma1, sigma2, expiry)
        var = u2 - u1**2
        
        if var <= 0:
            return np.nan
        
        m3Central = u3 - 3 * u1 ( u2 + 2 * (u1**3))
        return m3Central / (var **1.5)
        
        
if __name__ == '__main__':
    
    ml = MixLogNormal()
    
    # Option Price
    strike = 90
    intRate = 0.05
    expiry = 1
    w1 = 0.610
    f1 = 94.50
    f2 = 106.75
    sigma1 = 0.18
    sigma2 = 0.31
    modelType = 'black76'
    optionType = 'call'
    
    ml.OptionPrice(strike, intRate, expiry, w1, f1, f2, sigma1, sigma2, modelType, optionType)
    
    # Calibration
    strike = [90, 95, 100, 105, 110]
    marketPrice = [12, 8, 5, 3, 1.5]
    rate = [0.03, 0.03, 0.03, 0.03, 0.03]
    stockPrice = 100
    expiry = 1
    
    res = ml.Calibrate(stockPrice, marketPrice, strike, rate, expiry, 'Black-Scholes', 'call')
    w, f1, sigma1, sigma2 = res
    model_prices = [ml.OptionPrice(stockPrice, k, 0.05, 1, w, f1, sigma1, sigma2, 'Black-Scholes', 'call') for k in strike]
    
    # Moments
    price = 100
    moment1 = ml.FirstMoment(price, w1, f1, sigma1, sigma2, expiry)
    moment2 = ml.SecondMoment(price, w1, f1, sigma1, sigma2, expiry)
    moment3 = ml.ThirdMoment(price, w1, f1, sigma1, sigma2, expiry)
    
    # PDF and CDF
    price = 100
    expiry = 1
    w1 = 0.610
    f1 = 94.50
    f2 = 106.75
    sigma1 = 0.18
    sigma2 = 0.31
        
    ml.PDF(price, w1, f1, sigma1, sigma2, expiry)
    
    