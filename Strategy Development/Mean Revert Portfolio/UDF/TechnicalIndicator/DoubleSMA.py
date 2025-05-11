import pandas as pd

from UDF.TechnicalIndicator.ABCTechnicalIndicator import ABCTechnicalIndicator

class DoubleSMA(ABCTechnicalIndicator):
    def __init__(self, shortWindow = 10, longWindow = 30):
        self.shortWindow = shortWindow
        self.longWindow  = longWindow
    
    def Calculate(self, timeSeries):
        #df = pd.DataFrame({"total smooth": timeSeries})
        timeSeries['sma short'] = timeSeries['total smooth'].rolling(window=self.shortWindow).mean()
        timeSeries['sma long'] = timeSeries['total smooth'].rolling(window=self.longWindow).mean()
        
        return timeSeries