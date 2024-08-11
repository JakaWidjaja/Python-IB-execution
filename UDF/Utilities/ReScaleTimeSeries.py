import numpy as np

class ReScaleTimeSeries:
    def __init__(self):
        pass
        
    def Normalised(self, timeSeries):
        self.timeSeries = timeSeries
        
        minValue = min(self.timeSeries)
        maxValue = max(self.timeSeries)
        
        normTimeSeries = (self.timeSeries - minValue) / (maxValue - minValue)
        
        return normTimeSeries
    
    def NormalisedNegativePositive(self, timeSeries):
        self.timeSeries = timeSeries
        
        minValue = min(self.timeSeries)
        maxValue = max(self.timeSeries)
        
        ReScale = list(2 * (self.timeSeries - minValue) / (maxValue - minValue) - 1)
        
        return ReScale
    
    def NormalisedNegativePositiveReverse(self, timeSeries, reScaledPrice):
        self.timeSeries    = timeSeries
        self.reScaledPrice = reScaledPrice
        
        minValue = min(self.timeSeries)
        maxValue = max(self.timeSeries)
        
        unScaledPrice = minValue + ((reScaledPrice + 1) * (maxValue - minValue)) / 2.0
        
        return unScaledPrice
        
    
    def Standardised(self, timeSeries):
        self.timeSeries = timeSeries
        
        std  = np.std(self.timeSeries)
        mean = np.mean(self.timeSeries)
        
        stdTimeSeries = (self.timeSeries - mean) / std
        
        return stdTimeSeries

