from UDF.ReScaleTimeSeries.ABCScaler import ABCScaler

import numpy as np

class Standardised(ABCScaler):
    def __init__(self):
        pass

    def Scale(self, timeSeries):        
        std  = np.std(timeSeries)
        mean = np.mean(timeSeries)
        
        stdTimeSeries = (timeSeries - mean) / std
        
        return stdTimeSeries

