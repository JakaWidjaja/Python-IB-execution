from UDF.TechnicalIndicator.HurstExponent          import HurstExponent
from UDF.TechnicalIndicator.VarianceRatio          import VarianceRatio
from UDF.TechnicalIndicator.AutocovarianceFunction import AutocovarianceFunction
from UDF.TechnicalIndicator.HalfLife               import HalfLife
from UDF.TechnicalIndicator.DoubleSMA              import DoubleSMA

class TechnicalIndicator:
    def __init__(self):
        pass
    
    @staticmethod
    def Create(name, **kwargs):
        techIndicatorName = name.lower()
        
        if techIndicatorName == 'hurst exponent':
            return HurstExponent(**kwargs)
        
        elif techIndicatorName == 'variance ratio':
            return VarianceRatio(**kwargs)
        
        elif techIndicatorName == 'autocovariance':
            return AutocovarianceFunction(**kwargs)
        
        elif techIndicatorName == 'half-life':
            return HalfLife(**kwargs)
        
        elif techIndicatorName == 'doublesma':
            return DoubleSMA(**kwargs)
        
        else:
            raise ValueError(f" Unknown {name} method")
