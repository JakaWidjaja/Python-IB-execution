import numpy as np
from scipy.special import factorial, gamma, digamma

from UDF.Utilities import ReScaleTimeSeries

class BertramEntryExit:
    def __init__(self):
        pass
    
    def w1(self, z, tolerance = 1e-8):
        self.z         = z
        self.tolerance = tolerance
        
        total1 = 0.0
        total2 = 0.0
        sqrt2z = np.sqrt(2) * self.z
        k = 1
        
        while True:
            term1 = (sqrt2z ** k) / factorial(k) * gamma(k/2.0)
            term2 = (-sqrt2z ** k) / factorial(k) * gamma(k/2.0)
            
            total1 += term1
            total2 += term2
            
            #Break the while loop when no longer adding material gain
            if abs(total1 - total2) <= tolerance:
                break
            
            k += 1
            
        total1 = (total1 * 0.5) ** 2
        total2 = (total2 * 0.5) ** 2
        
        return total1 - total2
    
    def w2(self, z, tolerance):
        self.z         = z
        self.tolerance = tolerance
        
        # Set numpy to raise errors on overflow
        old_settings = np.seterr(over='raise')

        total = 0.0
        k = 1

        sqrt2z = np.sqrt(2) * self.z
        
        while True:
            const = 2 * k - 1
            constHalf = const / 2.0
            
            try:
                term = ((sqrt2z ** const) / factorial(const)) * gamma(constHalf) * digamma(constHalf)
            except FloatingPointError:
                break
            
            #Break the while loop when no longer adding material gain
            if abs(term) <= tolerance:
                break
            
            total += term
            k += 1
            
        # Restore numpy settings    
        np.seterr(**old_settings) 
        
        return total
        
    def VarT(self, entryPrice, exitPrice):
        self.entryPrice = entryPrice
        self.exitPrice  = exitPrice
        
        return self.w1(self.entryPrice) - self.w1(self.exitPrice) - self.w2(self.entryPrice) + self.w2(self.exitPrice)
      
    def ET(self, entryPrice, exitPrice, tolerance = 1e-8):
        self.entryPrice = entryPrice
        self.exitPrice = exitPrice
        self.tolerance = tolerance
        
        sqrt2 = np.sqrt(2)
        total = 0.0
        k = 1
        
        # Set numpy to raise errors on overflow
        old_settings = np.seterr(over='raise')
        
        while True:
            const = k * 2.0 - 1.0
            try:
                term = ((sqrt2 * self.entryPrice) ** const - (sqrt2 * self.exitPrice) ** const) / \
                        factorial(const + 1) * gamma(const / 2.0)
            except FloatingPointError:
                break
            
            if abs(term) < self.tolerance:
                break
            
            total += term
            k += 1
            
        # Restore numpy settings    
        np.seterr(**old_settings) 
        
        return total
        
    def ZM(self, entryPrice, exitPrice, costPrice, mu, theta, sigma):
        self.entryPrice = entryPrice
        self.exitPrice  = exitPrice
        self.costPrice  = costPrice
        self.mu         = mu
        self.theta      = theta
        self.sigma      = sigma
        
        if self.ET(self.entryPrice, self.exitPrice, self.costPrice, self.mu, self.theta, self.sigma) == 0:
            ZMAdjust = np.sqrt(2 / (self.theta * self.sigma**2)) * \
                                (self.exitPrice - self.entryPrice - self.costPrice)
        else:
            ZMAdjust = np.sqrt(2 / (self.theta * self.sigma**2)) * \
                (self.exitPrice - self.entryPrice - self.costPrice) / self.ET(self.entryPrice, self.exitPrice)
                
        return ZMAdjust

    def ZV(self, entryPrice, exitPrice, costPrice, sigma):
        self.entryPrice = entryPrice
        self.exitPrice  = exitPrice
        self.costPrice  = costPrice
        self.sigma      = sigma

        pi = self.exitPrice - self.entryPrice - self.costPrice
        denom = self.ET(self.entryPrice, self.exitPrice)
        if denom == 0:
            denom = 1
            
        try:
            ZVAdjust = (2.0 / (self.sigma ** 2)) * ((pi**2) / (denom**3)) * self.VarT(self.entryPrice, self.exitPrice)
        except FloatingPointError:
            ZVAdjust = (2.0 / (self.sigma ** 2)) * (pi**2) * self.VarT(self.entryPrice, self.exitPrice)
                                                    
        return ZVAdjust
    
    #Calibration function. maximize ZM
    def objective(self, x, costPrice, mu, theta, sigma):
        self.x         = x
        self.costPrice = costPrice
        self.mu        = mu
        self.theta     = theta
        self.sigma     = sigma
        
        entryPrice = self.x[0]
        exitPrice  = self.x[1]
        
        const = np.sqrt(2 * self.theta / (self.sigma**2))
        
        entryPriceAdjust = const * (entryPrice - self.mu)
        exitPriceAdjust  = const * (exitPrice  - self.mu)
        
        return -self.ZM(entryPriceAdjust, exitPriceAdjust, self.costPrice, self.mu, self.theta, self.sigma) * 1e5
    
        
        
        

















