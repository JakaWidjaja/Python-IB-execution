
from UDF.RiskNeutralDensity import BetaDensity

import numpy as np
from scipy.integrate import quad

class Beta:
    def __init__(self):
        pass
    
    def OptionPrice(self, strike, intRate, expiry, a, b, p, q):
        self.strike  = strike
        self.intRate = intRate
        self.expiry  = expiry
        self.a       = a
        self.b       = b
        self.p       = p
        self.q       = q
        
        density = BetaDensity.BetaDensity()
        
        discount = np.exp(-self.intRate * self.expiry)
        
        #Define integrand
        integrand = lambda s: max(s - self.strike, 0) * density.PDF(s, self.a, self.b, self.p, self.q)
        
        #Integrate
        price, _ = quad(integrand, self.strike, np.inf)
        
        return discount * price
        
        
        
        
        
        
        
        
        
        
        
        
        
        