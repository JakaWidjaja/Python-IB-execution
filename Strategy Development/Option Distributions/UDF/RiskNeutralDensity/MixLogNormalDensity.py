import numpy as np

from scipy.stats import norm


class MixLogNormalDensity:
    def __init__(self):
        pass
    
    def PDF(self, price, w1, f1, f2, sigma1, sigma2, expiry):
        self.price  = price  #Asset Price
        self.w1     = w1     #Weight of the first log normal
        self.f1     = f1     #Means of the first log normal
        self.f2     = f2     #Means of the second log normal
        self.sigma1 = sigma1 #Volatility of the first log normal
        self.sigma2 = sigma2 #volatility of the second log normal
        self.expiry = expiry #Option's time to expiry
        
        ln1 = norm.pdf(np.log(self.price), loc = np.log(self.f1) - 0.5 * self.sigma1**2 * self.expiry, 
                                           scale = self.sigma1 * np.sqrt(self.expiry)) / self.price
        
        ln2 = norm.pdf(np.log(self.price), loc = np.log(self.f2) - 0.5 * self.sigma2**2 * self.expiry, 
                                           scale = self.sigma1 * np.sqrt(self.expiry)) / self.price
        
        return self.w1 * ln1 + (1 - self.w1) * ln2
    
    def CDF(self, price, w1, f1, f2, sigma1, sigma2, expiry):
        self.price  = price  #Asset Price
        self.w1     = w1     #Weight of the first log normal
        self.f1     = f1     #Means of the first log normal
        self.f2     = f2     #Means of the second log normal
        self.sigma1 = sigma1 #Volatility of the first log normal
        self.sigma2 = sigma2 #volatility of the second log normal
        self.expiry = expiry #Option's time to expiry
        
        ln1 = norm.cdf(np.log(self.price), loc = np.log(self.f1) - 0.5 * self.sigma1**2 * self.expiry, 
                                           scale = self.sigma1 * np.sqrt(self.expiry))
        
        ln2 = norm.cdf(np.log(self.price), loc = np.log(self.f2) - 0.5 * self.sigma2**2 * self.expiry, 
                                           scale = self.sigma2 * np.sqrt(self.expiry))
        
        return self.w1 * ln1 + (1 - self.w2) * ln2
            
        
if __name__ == '__main__':
    
    ml = MixLogNormalDensity()
    
    price = 100
    expiry = 1
    w1 = 0.610
    f1 = 94.50
    f2 = 106.75
    sigma1 = 0.18
    sigma2 = 0.31
        
    ml.PDF(price, w1, f1, f2, sigma1, sigma2, expiry)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        