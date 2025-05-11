import numpy as np
from scipy.optimize import fsolve

class OptionUpperLowerBound:
    def __init__(self):
        pass
    
    def TwoMomentsMode(self, price, strike, vol, rate, expiry):
        self.price  = price
        self.strike = strike
        self.vol    = vol
        self.rate   = rate
        self.expiry = expiry
        
        mu1  = self.FirstMoment(self.rate, self.expiry)            #First moment
        mu2  = self.SecondMoment(self.vol, self.rate, self.expiry) #Second moment
        mode = self.Mode(self.vol, self.rate, self.expiry)         #Mode

        #Transform the moments for Khinchin's method
        nu1 = 2.0 * mu1 - mode
        nu2 = 3.0 * mu2 - 2.0 * nu1 * mode

        #Upper and lower bounds
        if self.price <= self.strike / mode: #Case 1
            if self.price <= self.strike / nu1:
                lowerBound = 0.0
            else:
                lowerBound = mu1 * self.price - self.strike + (self.strike - self.price * mode)**2 / (2 * self.price * (nu1 - mode))
                
            if self.price <= (nu1 * (3 * nu2 - 2 * mode * nu1)) / nu2**2 * self.strike:
                y = [1, 
                     -3 * self.strike, 
                     (4 * nu1 + 2 * mode) * self.price * self.strike - (2 * mode * nu1 + nu2) * self.price**2,
                     2 * mode * nu2 * self.price**3 - (2 * mode * nu1 + nu2) * self.price**2 * self.strike]
                y = self.cubicRoot(y, max(self.strike, nu2 / nu1 * self.price))
                
                upperBound = self.price**2 * (nu2 - nu1**2) * (y - self.strike)**2 / \
                            (2 * (self.price**2 * (nu2 - nu1**2) + (y - nu1 * self.price)**2) * (y - mode * self.price))
            else:
                upperBound = nu1 * (nu2 * self.price - nu1 * self.strike)**2 / (2 * self.price * nu2 * (nu2 - mode * nu1))
                
        else:
            lowerBound = mu1 * self.price - self.strike
            
            if self.price <= (2 * mode * nu1 + nu2) / (2 * mode * nu2) * self.strike:
                z = [1, 
                     -3 * self.strike, 
                     (4 * nu1 + 2 * mode) * self.price * self.strike - (2 * mode * nu1 + nu2) * self.price**2,
                     2 * mode * nu2 * self.price**3 - (2 * mode * nu1 + nu2) * self.price**2 * self.strike]
                z = self.CubicRoot(z, max(0, self.strike))
                
                upperBound = mu1 * self.price - self.strike + self.price**2 * (nu2 - nu1**2) * (z - self.strike)**2 / \
                            (2 * (self.price**2 * (nu2 - nu1**2) + (z - nu1 * self.price)**2) * (mode * self.price - z))
            else:
                upperBound = mu1 * self.price - self.strike + self.strike**2 / (2 * mode * self.price) * (nu2 - nu1**2) / nu2
            
        lowerBound *= np.exp(-self.rate * self.expiry)
        upperBound *= np.exp(-self.rate * self.expiry)
        
        return lowerBound, upperBound

    def ThreeMoments(self, price, strike, vol, rate, expiry):
        self.price  = price
        self.strike = strike
        self.vol    = vol
        self.rate   = rate
        self.expiry = expiry
        
        discount = np.exp(-self.rate * self.expiry)
        
        mu1 = self.FirstMoment(self.rate, self.expiry)            # First moment
        mu2 = self.SecondMoment(self.vol, self.rate, self.expiry) # Second moment
        mu3 = self.ThirdMoment(self.vol, self.rate, self.expiry)  # Third moment
        
        #p function
        p = lambda x: (mu2 - mu1**2) * x**2 + (mu1 * mu2 - mu3) * x + (mu1 * mu3 - mu2**2)
        
        #Calculate the v and w         
        coeff = [mu2 - mu1**2, 
                 mu1 * mu2 - mu3, 
                 mu1 * mu3 - mu2**2]
        v, w = self.SquareRoot(coeff)
        if v > w:
            v, w = w, v
            
        #Calculate the q variable
        coeff = [1, 
                 (-2.0 * mu2 * self.price + 3.0 * mu1 * self.strike) / (2.0 * mu1 * self.price), 
                 (2.0 * mu2 * self.strike) / (mu1 * self.price), 
                 (-mu3 * self.strike) / (2.0 * mu1 * self.price)]
        q = self.CubicRoot(coeff, w)

        #Lower Bound
        if self.price < (mu1/mu2 * self.strike):
            lowerBound = 0.0
        elif self.price >= (mu1/mu2 * self.strike) and self.price <= (self.strike / v):
            lowerBound = mu1 * self.price - self.strike + (-p(self.strike) * self.price**2) / (mu3 * self.price - mu2 * self.strike)
        elif self.price > self.strike / v:
            lowerBound = mu1 * self.price - self.strike
            
        #Upper Bound
        if self.price < (3 * w - v) / (2 * w**2) * self.strike:
            upperBound = (mu3 * mu1 - mu2**2) / (mu3 - 2 * q * mu2 + q**2 * mu1) * (q * self.price - self.strike) / q
        elif self.price >= (3 * w - v) / (2 * w**2) * self.strike and self.price < 2/(v + w) * self.strike:
            upperBound = (mu3 * mu1 - mu2**2) / (mu3 - 2 * w * mu2 + w**2 * mu1) * (w * self.price - self.strike) / w
        elif self.price >= 2 / (v + w) * self.strike and self.price < (2 * mu1) / mu2 * self.strike:
            upperBound = 0.5 * (mu1 * self.price - self.strike) + 0.5 * np.sqrt(self.price**2 * (mu2 - mu1**2) + (mu1 * self.price - self.strike)**2)
        elif self.price >= 2 * mu1 / mu2 * self.strike:
            upperBound = mu1 * self.price - mu1**2 / mu2 * self.strike
            
        return discount * lowerBound, discount * upperBound
            
    def TwoMoments(self, price, strike, vol, rate, expiry):
        self.price  = price
        self.strike = strike
        self.vol    = vol
        self.rate   = rate
        self.expiry = expiry
        
        discount = np.exp(-self.rate * self.expiry)
        
        mu1 = self.FirstMoment(self.rate, self.expiry)            # First moment
        mu2 = self.SecondMoment(self.vol, self.rate, self.expiry) # Second moment
        
        #Lower Bound
        if self.price <= self.strike / mu1:
            lowerBound = 0
        elif self.price > self.strike / mu1:
            lowerBound = mu1 * self.price - self.strike
            
        #Upper Bound
        if self.price <= 2.0 * mu1 / mu2 * self.strike:
            upperBound = 0.5 * (mu1 * self.price - self.strike) + 0.5 * np.sqrt(self.price**2 * (mu2 - mu1**2) + (mu1 * self.price - self.strike)**2)
        elif self.price > 2.0 * mu1 / mu2 * self.strike:
            upperBound = mu1 * self.price - mu1**2 / mu2 * self.strike
            
        return discount * lowerBound, discount * upperBound
        
        
    def FirstMoment(self, rate, expiry):
        self.rate   = rate
        self.expiry = expiry
        
        mu1 = np.exp(self.rate * self.expiry)
        
        return mu1
        
    def SecondMoment(self, vol, rate, expiry):
        self.vol    = vol
        self.rate   = rate
        self.expiry = expiry
        
        mu2 = np.exp(2.0 * self.rate * self.expiry + self.vol**2 * self.expiry)
        
        return mu2
    
    def ThirdMoment(self, vol, rate, expiry):
        self.vol    = vol
        self.rate   = rate
        self.expiry = expiry
        
        mu3 = np.exp(3.0 * self.rate * self.expiry + 3.0 * self.vol**2 * self.expiry)
        
        return mu3
    
    def Mode(self, vol, rate, expiry):
        self.vol    = vol
        self.rate   = rate
        self.expiry = expiry
        
        mode = np.exp(self.rate * self.expiry - self.vol**2 * self.expiry)
        
        return mode
    
    def SquareRoot(self, coeffs):
        self.coeffs = coeffs
        
        a, b, c = self.coeffs
        discriminant = b**2 - 4*a*c
        if discriminant < 0:
            raise ValueError("The quadratic equation has no real roots.")
    
        root1 = (-b + np.sqrt(discriminant)) / (2 * a)
        root2 = (-b - np.sqrt(discriminant)) / (2 * a)
        
        return root1, root2
    
    def CubicRoot(self, coeffs, start):
        self.coeffs = coeffs
        self.start  = start
        
        def cubic(x):
            return self.coeffs[0] * x**3 + self.coeffs[1] * x**2 + self.coeffs[2] * x + self.coeffs[3]
        
        root = fsolve(cubic, start)[0]
        return root
    
    
if __name__ == '__main__':
     
    price  = 229.67
    strike = 225
    rate   = 0.04896290863630161
    expiry = 0.1178082191780822
    vol    = 0.269150260957715

    opt = OptionUpperLowerBound()
    opt.ThreeMoments(price, strike, vol, rate, expiry)

    # Debugging intermediate values
    mu1 = opt.FirstMoment(rate, expiry)
    mu2 = opt.SecondMoment(vol, rate, expiry)
    mu3 = opt.ThirdMoment(vol, rate, expiry)
    mode = opt.Mode(vol, rate, expiry)
    nu1 = 2.0 * mu1 - mode
    nu2 = 3.0 * mu2 - 2.0 * nu1 * mode
    
    print(f"First Moment (μ1): {mu1:.4f}")
    print(f"Second Moment (μ2): {mu2:.4f}")
    print(f"Mode: {mode:.4f}")
    print(f"Transformed Moment (ν1): {nu1:.4f}")
    print(f"Transformed Moment (ν2): {nu2:.4f}")
    
    p = lambda x: (mu2 - mu1**2) * x**2 + (mu1 * mu2 - mu3) * x + (mu1 * mu3 - mu2**2)
    v = 0.9247397524597991
    w = 1.1127649785170868
    if price < (mu1/mu2 * strike):
        lowerBound = 0.0
    elif price >= (mu1/mu2 * strike) and price <= (strike / v):
        lowerBound = mu1 * price - strike + (-p(strike) * price**2) / (mu3 * price - mu2 * strike)
    elif price > strike / v:
        lowerBound = mu1 * price - strike
    
    x = strike
    