import numpy  as np
import pandas as pd

from UDF.TechnicalIndicator.ABCTechnicalIndicator import ABCTechnicalIndicator

class VarianceRatio(ABCTechnicalIndicator):
    def __init__(self, lag):
        self.lag = lag
        
    def Calculate(self, timeSeries):
        series = pd.Series(timeSeries).dropna()
        n = len(series)
        
        mu = np.mean(np.diff(series))
        m = (n - self.lag + 1) * (1 - self.lag / n)
        
        b = np.sum((np.diff(series) - mu)**2) / (n - 1)
        t = np.sum((series[self.lag:].reset_index(drop = True) - series[:-self.lag].reset_index(drop = True) - self.lag * mu)**2) / m
        
        vr = t / (self.lag * b)
        
        return vr