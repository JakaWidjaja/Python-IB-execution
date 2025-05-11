from UDF.OptionPricer import BlackScholes
from UDF.OptionPricer import Black76

class MixLogNormal:
    def __init__(self):
        pass
    
    def OptionPrice(self, strike, intRate, expiry, w1, f1, f2, sigma1, sigma2, modelType, optionType):
        self.strike     = strike
        self.intRate    = intRate
        self.expiry     = expiry
        self.w1         = w1
        self.f1         = f1
        self.f2         = f2
        self.sigma1     = sigma1
        self.sigma2     = sigma2
        self.modelType  = modelType
        self.optionType = optionType
        
        if self.modelType.lower() == 'black-scholes':
            bl  = BlackScholes.BlackScholes()
            price1 = bl.Price(self.f1, self.strike, self.sigma1, self.expiry, self.intRate, self.optionType)
            price2 = bl.Price(self.f2, self.strike, self.sigma2, self.expiry, self.intRate, self.optionType)

            return self.w1 * price1 + (1-self.w1) * price2
        
        elif self.modelType.lower() == 'black76':
            b76 = Black76.Black76()
            price1 = b76.Price(self.f1, self.strike, self.sigma1, self.expiry, self.intRate, self.optionType)
            price2 = b76.Price(self.f2, self.strike, self.sigma2, self.expiry, self.intRate, self.optionType)

            return self.w1 * price1 + (1-self.w1) * price2
        
if __name__ == '__main__':
    
    ml = MixLogNormal()
    
    strike = 90
    intRate = 0.05
    expiry = 1
    w1 = 0.610
    f1 = 94.50
    f2 = 106.75
    sigma1 = 0.18
    sigma2 = 0.31
    modelType = 'black76'
    optionType = 'call'
    
    ml.OptionPrice(strike, intRate, expiry, w1, f1, f2, sigma1, sigma2, modelType, optionType)
