from UDF.ReScaleTimeSeries.ABCScaler import ABCScaler

class Normalised(ABCScaler):
    def __init__(self):
        pass

    def Scale(self, timeSeries):        
        minValue = min(timeSeries)
        maxValue = max(timeSeries)
        
        normTimeSeries = (timeSeries - minValue) / (maxValue - minValue)
        
        return normTimeSeries