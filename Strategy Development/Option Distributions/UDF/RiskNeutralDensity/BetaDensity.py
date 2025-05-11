
from scipy.special import gamma

class BetaDensity:
    def __init__(self):
        pass
    
    def PDF(self, price, a, b, p, q):
        self.price = price
        self.a     = a     #Shape
        self.b     = b     #Scale
        self.p     = p     #First shape 
        self.q     = q     #Second shape
        
        if price <= 0:
            return 0.0
        
        betaFunction = gamma(self.p) * gamma(self.q) / gamma(self.p + self.q)
        
        numerator = self.a * self.price**(self.a * self.p - 1.0)
        
        denominator = (self.b**(self.a * self.p)) * betaFunction * (1 + (self.price / self.b)**self.a)**(self.p + self.q)
        
        return numerator / denominator
    
if __name__ == '__main__':
    
    be = BetaDensity()
    
    a, b, p, q = 2.0, 150.0, 3.0, 4.0
    price = 140
    
    be.PDF(price, a, b, p, q)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
