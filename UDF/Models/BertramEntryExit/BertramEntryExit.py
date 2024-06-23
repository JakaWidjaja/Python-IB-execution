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
      
        
        



















