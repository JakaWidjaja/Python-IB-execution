from UDF.ReScaleTimeSeries.ABCScaler import ABCScaler

class NormalisedPlusMinus(ABCScaler):
    def __init__(self):
        pass
    
    def Scale(self, timeSeries, **kwargs):
        number = kwargs.get('number', 1)        
        minValue = min(timeSeries)
        maxValue = max(timeSeries)
        
        ReScale = list(2 * (timeSeries - minValue) / (maxValue - minValue) - 1)
        
        return ReScale * number

