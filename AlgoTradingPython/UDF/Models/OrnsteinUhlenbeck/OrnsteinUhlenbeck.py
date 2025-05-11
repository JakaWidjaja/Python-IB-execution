import numpy as np

from UDF.Models.OrnsteinUhlenbeck.MethodMoment import MethodMoment
from UDF.Models.OrnsteinUhlenbeck.MaxLikelihood import MaxLikelihood

class OrnsteinUhlenbeck(object):
    '''
    dp = t (u - p) dt + sigma dw
    u = long term mean
    t = speed
    '''
    def __init__(self):
        pass
        
    def Moment(self, timeSeries):
        self.timeSeries = np.array(timeSeries)
        
        calibrateParameter = MethodMoment(self.timeSeries)
        mu, theta, sigma = calibrateParameter.parameter()
        
        return mu, theta, sigma
    
    def MaxLikelihood(self, timeSeries):
        self.timeSeries = np.array(timeSeries)
        
        calibrateParameter = MaxLikelihood(self.timeSeries)
        mu, theta, sigma = calibrateParameter.parameter()
        
        # mu - long term mean
        # theta - speed of mean reversion
        return mu, theta, sigma
    
    #def max_pl_expectation(self, weight):
        