import statsmodels.api as sm
import pandas          as pd
import numpy           as np

from UDF.TechnicalIndicator.ABCTechnicalIndicator import ABCTechnicalIndicator

class HalfLife(ABCTechnicalIndicator):
    def __init__(self):
        pass
    
    def Calculate(self, timeSeries):
        series = pd.Series(timeSeries)
        laggedSeries = series.shift(1).dropna()
        deltaSeries = series.diff().dropna()

        laggedSeries = laggedSeries.loc[deltaSeries.index]

        model = sm.OLS(deltaSeries, sm.add_constant(laggedSeries))
        result = model.fit()
        
        lambda_ = result.params.iloc[-1]
        half_life = -np.log(2) / lambda_

        return half_life  






