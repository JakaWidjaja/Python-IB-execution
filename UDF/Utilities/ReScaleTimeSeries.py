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
    
    def Standardised(self, timeSeries):
        self.timeSeries = timeSeries
        
        std  = np.std(self.timeSeries)
        mean = np.mean(self.timeSeries)
        
        stdTimeSeries = (self.timeSeries - mean) / std
        
        return stdTimeSeries

