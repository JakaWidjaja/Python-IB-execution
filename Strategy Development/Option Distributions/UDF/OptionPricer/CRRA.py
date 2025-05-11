import numpy as np
from scipy.integrate import quad

from UDF.RealWorldDensity import CRRAUtility

class CRRA:
    def __init__(self):
        self.crraDensity = CRRAUtility.CRRAUtility()
    
    def MixLogNormalOptionPrice(self, strike, intRate, expiry, optionType, riskAversion, w1, f1, f2, sigma1, sigma2):
        self.strike = strike
        self.intRate = intRate
        self.expiry = expiry
        self.optionType = optionType
        self.riskAversion = riskAversion 
        self.w1     = w1     #Weight of the first log normal
        self.f1     = f1     #Means of the first log normal
        self.f2     = f2     #Means of the second log normal
        self.sigma1 = sigma1 #Volatility of the first log normal
        self.sigma2 = sigma2 #volatility of the second log normal
        
        discount = np.exp(-self.intRate * self.expiry)
        
        if self.optionType.lower() == 'call':
            payoff = lambda price: max(price - self.strike, 0)
        elif self.optionType.lower() == 'put':
            payoff = lambda price: max(self.strike - price, 0)
        else:
            raise ValueError("Invalid option type. Use 'call' or 'put'.")
            
        #integrand for the option price
        integrand = lambda price: payoff(price) * self.crraDensity.MixLogNormalPDF(price, self.riskAversion, 
                                                                              self.w1, self.f1, self.f2, self.sigma1, self.sigma2, self.expiry)
        
        #Numerical integration
        optionPrice, _ = quad(integrand, 0, np.inf)
        
        return discount * optionPrice
    
    def BetaOptionPrice(self, strike, intRate, expiry, optionType, riskAversion, a, b, p, q):
        self.strike       = strike
        self.intRate      = intRate
        self.expiry       = expiry
        self.optionType   = optionType
        self.riskAversion = riskAversion
        self.a            = a
        self.b            = b
        self.p            = p
        self.q            = q
        
        discount = np.exp(-self.intRate * self.expiry)

        def payoff(price):
            if self.optionType.lower() == 'call':
                return max(price - self.strike, 0)
            elif self.optionType.lower() == 'put':
                return max(self.strike - price, 0)
            else:
                raise ValueError("Invalid option type. Use 'call' or 'put'.")

        def integrand(price):
            return payoff(price) * \
                    self.crraDensity.BetaPDF(price, self.riskAversion, self.a, self.b, self.p, self.q)
        
        optionPrice, _ = quad(integrand, 0, np.inf)

        return discount * optionPrice
        
if __name__ == '__main__':
    
    opt = CRRA()
    
    strike = 77
    intRate = 0.05
    expiry = 1
    w1 = 0.610
    f1 = 94.50
    f2 = 106.75
    sigma1 = 0.18
    sigma2 = 0.31
    optionType = 'call'
    riskAversion = 0.5
    
    opt.MixLogNormalOptionPrice(strike, intRate, expiry, optionType, riskAversion, w1, f1, f2, sigma1, sigma2)
    
    
    a, b, p, q = 2.0, 150.0, 3.0, 4.0  # Beta density parameters
    riskAversion = 2.0  # Risk aversion parameter (CRRA)
    intRate = 0.05
    expiry = 1
    strike = 140 
    
    opt.BetaOptionPrice(strike, intRate, expiry, optionType, riskAversion, a, b, p, q)
