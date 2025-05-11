import numpy as np

from UDF.TechnicalIndicator.ABCTechnicalIndicator import ABCTechnicalIndicator

class HurstExponent(ABCTechnicalIndicator):
    def __init__(self, maxLag):
        self.maxLag = maxLag
        
    def Calculate(self, timeSeries):
        lags = np.arange(2, self.maxLag)
        tau = [np.std(np.subtract(timeSeries[l:], timeSeries[:-l])) for l in lags]
        
        poly = np.polyfit(np.log(lags), np.log(tau), 1)
        
        # Hirst exponent is the slope
        hurst = poly[0]
        
        return hurst
