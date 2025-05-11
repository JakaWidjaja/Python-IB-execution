
from UDF.RealWorldDensity import CRRAUtility

from scipy.optimize import minimize
import numpy as np

class CalibrateCRRA:
    def __init__(self):
        pass
    
    def CalibrateMixLogNormal(self, marketPrices, w1, f1, f2, sigma1, sigma2, expiry):
        self.marketPrices = marketPrices #Realised or projected market prices. 
        self.w1     = w1     #Weight of the first log normal
        self.f1     = f1     #Means of the first log normal
        self.f2     = f2     #Means of the second log normal
        self.sigma1 = sigma1 #Volatility of the first log normal
        self.sigma2 = sigma2 #volatility of the second log normal
        self.expiry = expiry #Option's time to expiry
        
        crra = CRRAUtility.CRRAUtility()
        
        def error(x):
            
            likelihoods = [crra.MixLogNormalPDF(price, x[0], self.w1, self.f1, self.f2, self.sigma1, self.sigma2, self.expiry) for price in self.marketPrices]
            
            return -sum(np.log(likelihoods))
        
        init = [2.5]
        bnd = [(0,5)]
        
        res = minimize(error, x0 = init, bounds = bnd, method = 'trust-constr')
        
        return res.x[0]
        
if __name__ == '__main__': 
        
    calib = CalibrateCRRA()
    
    expiry = 1
    w1 = 0.610
    f1 = 94.50
    f2 = 106.75
    sigma1 = 0.18
    sigma2 = 0.31
    marketPrices = [100, 97, 94, 91, 88, 85, 82, 79, 76]
    
    calib.CalibrateMixLogNormal(marketPrices, w1, f1, f2, sigma1, sigma2, expiry)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        