import sys
sys.path.append("/home/lun/Desktop/Folder 2/Python_Model/OptionPricing")

import Black76      as bl76
import BlackScholes as bs
import MixLogNormal as mixLog

class OptionPricing:
    def __init__(self, modelType):
        self.modelType = modelType
        
        # Initiale the model
        if modelType == 'Black76':
            self.vanillaModel = bl76.Black76()
        elif modelType == 'BlackScholes' or 'Black-Scholes':
            self.vanillaModel = bs.BlackScholes()
        elif modelType == 'MixLogNormal':
            self.mixLogmodel = mixLog.MixLogNormal()
    
    # Vanilla Option models (i.e., Black-Scholes, Black76)
    def VanillaPrice(self, underlyingPrice, strike, vol, expiry, rate, optType, outputType):

        return self.model.Price(underlyingPrice, strike, vol, expiry, rate, optType)
    
    def VanillaImpliedVol(self, marketPrice, underlyingPrice, strike, expiry, rate, optType):
        
        return self.model.ImpliedVol(marketPrice, underlyingPrice, strike, expiry, rate, optType)
    
    def VanillaDelta(self):
        pass
    
    def VanillaGamma(self):
        pass
    
    def VanillaTheta(self):
        pass
    
    # Mix-LogNormal model
    def MixLogPrice(self, strike, rate, expiry, weight1, price1, price2, sigma1, sigma2, modelType, optionType):
        return self.mixLogModel.OptionPrice(strike, rate, expiry, weight1, price1, sigma1, sigma2, modelType, optionType)