import numpy as np
from scipy.integrate import quad

from UDF.RiskNeutralDensity import MixLogNormalDensity
from UDF.RiskNeutralDensity import BetaDensity

class CRRAUtility:
    def __init__(self):
        pass
    
    def MixLogNormalPDF(self, price, riskAversion, w1, f1, f2, sigma1, sigma2, expiry):
        self.price          = price
        self.riskAversion   = riskAversion
        self.w1             = w1     #Weight of the first log normal
        self.f1             = f1     #Means of the first log normal
        self.f2             = f2     #Means of the second log normal
        self.sigma1         = sigma1 #Volatility of the first log normal
        self.sigma2         = sigma2 #volatility of the second log normal
        self.expiry         = expiry #Option's time to expiry
        
        ml = MixLogNormalDensity.MixLogNormalDensity()
        
        riskNeutralPDF = lambda x: ml.PDF(x, self.w1, self.f1, self.f2, self.sigma1, self.sigma2, self.expiry)
        
        integrand = lambda y: y**self.riskAversion * riskNeutralPDF(y)

        normalised = quad(integrand, 0, np.inf)[0]
        
        return self.price**self.riskAversion * riskNeutralPDF(self.price) / normalised
    
    def MixLogNormalVol(self, riskAversion, w1, f1, f2, sigma1, sigma2, expiry):
        self.riskAversion = riskAversion
        self.w1 = w1
        self.f1 = f1
        self.f2 = f2
        self.sigma1 = sigma1
        self.sigma2 = sigma2
        self.expiry = expiry
        
        ml = MixLogNormalDensity.MixLogNormalDensity()
        
        riskNeutralPDF = lambda x: ml.PDF(x, self.w1, self.f1, self.f2, self.sigma1, self.sigma2, self.expiry)
        
        #Real world PDF
        crraPDF = lambda x: (x**self.riskAversion * riskNeutralPDF(x)) / quad(lambda y: y**self.riskAversion * riskNeutralPDF(y), 0, np.inf)[0]
        
        #Expected values
        expectS = quad(lambda x: x * crraPDF(x), 0, np.inf)[0]
        expectS2 = quad(lambda x: x**2 * crraPDF(x), 0, np.inf)[0]
        
        return np.sqrt(expectS2 - expectS**2)
    
    def BetaPDF(self, price, riskAversion, a, b, p, q):
        self.price        = price
        self.riskAversion = riskAversion
        self.a            = a
        self.b            = b
        self.p            = p
        self.q            = q
    
        beta = BetaDensity.BetaDensity()
        
        integrand = lambda y: y**self.riskAversion * beta.PDF(y, self.a, self.b, self.p, self.q)
        
        normalised = quad(integrand, 0, np.inf)[0]
        
        return (self.price**self.riskAversion * beta.PDF(self.price, self.a, self.b, self.p, self.q)) / normalised
    
    def BetaVol(self, riskAversion, a, b, p, q):
        self.riskAversion = riskAversion
        self.a            = a
        self.b            = b
        self.p            = p
        self.q            = q

        beta = BetaDensity.BetaDensity()
        riskNeutralPDF = lambda x: beta.PDF(x, self.a, self.b, self.p, self.q)

        # Real-world PDF
        crraPDF = lambda x: (x**self.riskAversion * riskNeutralPDF(x)) / quad(lambda y: y**self.riskAversion * riskNeutralPDF(y), 0, np.inf)[0]

        # Expected values
        expectS = quad(lambda x: x * crraPDF(x), 0, np.inf)[0]
        expectS2 = quad(lambda x: x**2 * crraPDF(x), 0, np.inf)[0]

        # Volatility
        return np.sqrt(expectS2 - expectS**2)
    
    
if __name__ == '__main__':
    
    cr = CRRAUtility()
    
    riskAversion = 1
    
    price = 100
    expiry = 1
    w1 = 0.610
    f1 = 94.50
    f2 = 106.75
    sigma1 = 0.18
    sigma2 = 0.31
    
    cr.MixLogNormalPDF(price, riskAversion, w1, f1, f2, sigma1, sigma2, expiry)
    
    
    
    a, b, p, q = 2.0, 150.0, 3.0, 4.0  # Example shape and scale parameters
    riskAversion = 2.0  # Risk aversion parameter
    price = 140  # Asset price
    
    cr.BetaPDF(price, riskAversion, a, b, p, q)
    

