import numpy as np
from scipy.stats import norm
from scipy.optimize import minimize
from scipy.integrate import quad

from UDF.OptionPricer import BlackScholes, Black76

class ExpectedProfitLoss:
    def __init__(self):
        pass
    
    def ExpectedPL(self, stock, expiry, rate, mu, sigma):
        self.stock   = stock
        self.expiry  = expiry
        self.rate    = rate
        self.mu      = mu
        self.sigma   = sigma
        
        lowerLimit = self.stock * np.exp(self.rate * self.expiry)
        lowerLimitNegative = -np.inf
        upperLimit = np.inf
        
        def profitIntegrand(stockPlusH):
            cdf = self.CDF(self.stock, stockPlusH, self.expiry, self.mu, self.sigma)
            return (stockPlusH * np.exp(-self.rate * self.expiry) - self.stock) * cdf #if stockPlusH > self.stock else 0
        
        def lossIntegrand(stockPlusH):
            cdf = self.CDF(self.stock, stockPlusH, self.expiry, self.mu, self.sigma)
            return (self.stock - stockPlusH * np.exp(-self.rate * self.expiry)) * cdf #if stockPlusH < self.stock else 0

        EP, _ = quad(profitIntegrand, lowerLimit, upperLimit)
        EL, _ = quad(lossIntegrand, 10, lowerLimit)
        print(quad(lossIntegrand, 10, lowerLimit))
        
        return EP, EL
    
    def CDF(self, stock, stockFuture, expiry, mu, sigma):
        self.stock       = stock
        self.stockFuture = stockFuture
        self.expiry      = expiry
        self.mu          = mu
        self.sigma       = sigma

        z = (np.log(self.stockFuture / self.stock) - (self.mu - 0.5 * self.sigma**2) * self.expiry) / (self.sigma * np.sqrt(self.expiry))
        
        return norm.cdf(z)
    
    def Calibrate(self, stock, optionData, expiry, rate):
        self.stock      = stock
        self.optionData = optionData
        self.expiry     = expiry
        self.rate       = rate

        def ssd(params):
            mu, sigma = params
            totalSSD = 0.0
            
            for opt in self.optionData:
                strike, marketPrice, optType, weight = opt
                
                b = (np.log(strike / self.stock) - (mu - 0.5 * sigma**2) * self.expiry) / (sigma * np.sqrt(self.expiry))
                
                if optType == 'call':
                    modelPrice = self.stock * np.exp((mu - self.rate) * self.expiry) * (1 - norm.cdf(b - sigma * np.sqrt(self.expiry))) - \
                        strike * np.exp(-self.rate * self.expiry) * norm.cdf(-b)
                else:
                    modelPrice = -self.stock * np.exp((mu - self.rate) * self.expiry) * (1 - norm.cdf(b - sigma * np.sqrt(self.expiry))) + \
                        strike * np.exp(-self.rate * self.expiry) * norm.cdf(-b)


                totalSSD += weight * (marketPrice - modelPrice)**2
            
            return totalSSD
        
        initGuess = [0.005, 0.20]
        bounds = [(-1, 1), (1e-6, None)]
        
        # Optimise
        res = minimize(ssd, initGuess, bounds = bounds, method="L-BFGS-B")
        print(res)
        return res.x

        
if __name__ == "__main__":
    # Inputs
    S = 100  # Current stock price
    T = 1    # Time to maturity (in years)
    r = 0.05 # Risk-free rate

    # Example option market data: (strike price, market price, type, weight)
    option_data = [
        (90, 15, "call", 1.0),
        (100, 10, "call", 1.0),
        (110, 5, "call", 1.0),
        (90, 8, "put", 1.0),
        (100, 10, "put", 1.0),
        (110, 15, "put", 1.0),
    ]
    
    option_data = [
        (90, 15, "call", 1.0),
        (100, 10, "call", 1.0),
        (110, 5, "call", 1.0),
    ]
    weights = [1.0] 
    
    model = ExpectedProfitLoss()
    
    params = [model.Calibrate(S, option_data, T, r)]  # Single set of parameters for simplicity
    
    model.ExpectedPL(S, T, r, params, weights)
    

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        