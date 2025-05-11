from UDF.ReScaleTimeSeries.Normalised          import Normalised
from UDF.ReScaleTimeSeries.NormalisedPlusMinus import NormalisedPlusMinus
from UDF.ReScaleTimeSeries.Standardised        import Standardised

class ReScaleTimeSeries:
    def __init__(self):
        pass
    
    @staticmethod
    def Create(methodName):
        name = methodName.lower()
        
        if name == 'normalised':
            return Normalised()
        
        elif name == 'normalisedplusminus':
            return NormalisedPlusMinus()
        
        elif name == 'standardised':
            return Standardised()
        
        else:
            raise ValueError(f'Unknown {methodName} model')
