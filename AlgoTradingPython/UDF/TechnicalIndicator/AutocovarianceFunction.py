import pandas as pd

from UDF.TechnicalIndicator.ABCTechnicalIndicator import ABCTechnicalIndicator

class AutocovarianceFunction(ABCTechnicalIndicator):
    def __init__(self, lag):
        self.lag = lag
        
    def Calculate(self, timeSeries):
        series = pd.Series(timeSeries)
        
        values = [series.autocorr(l) for l in range(1, self.lag + 1)]
        
        return values
        
        