from math import log, exp, sqrt
import numpy as np

class MaxLikelihood:
    '''
    Ornstein Uhlenbeck model. 
    Calibrated using Maximum Likelihood
    '''
    
    def __init__(self, timeSeries):
        '''
        time_series: an array of time series. 
        '''
        self.timeSeries = np.array(timeSeries)
        
        self.timeDelta =  1/len(self.timeSeries)
        self.n = len(self.timeSeries) #the number of data in the time series. 

    def Xx(self):
        
        return sum(self.timeSeries[0:len(self.timeSeries)-1])
    
    def Xy(self):
        
        return sum(self.timeSeries[1:self.n])
    
    def Xxx(self):
        
        return sum([self.timeSeries[i]**2 for i in range(0,self.n-1)])
    
    def Xxy(self):
        
        return sum([self.timeSeries[i-1] * self.timeSeries[i] for i in range(1, self.n)])
    
    def Xyy(self):
        
        return sum([self.timeSeries[i]**2.0 for i in range(1, self.n)])
    
    def theta(self):
        
        output = (self.Xy() * self.Xxx() - self.Xx() * self.Xxy()) / \
        (self.n * (self.Xxx() - self.Xxy()) - (self.Xx()**2.0 - self.Xx() * self.Xy()))
        
        return output
    
    def mu(self):
        
        output = -1.0 / self.timeDelta * \
                log((self.Xxy() - self.theta() * self.Xx() - self.theta() * self.Xy() + self.n * self.theta()**2.0) / 
                    (self.Xxx() - 2.0 * self.theta() * self.Xx() + self.n * self.theta()**2.0))
                
        return output
    
    def var(self):
        #Variance
        output = (2.0 * self.mu()) / (self.n * (1.0 - exp(-2 * self.mu() * self.timeDelta))) * \
                (self.Xyy() - 2.0 * exp(-self.mu() * self.timeDelta) * self.Xxy() + 
                exp(-2.0 * self.mu() * self.timeDelta) * self.Xxx() - \
                2 * self.theta() * (1.0 - exp(-self.mu() * self.timeDelta)) * \
                (self.Xy() - exp(-self.mu() * self.timeDelta) * self.Xx()) + \
                self.n * self.theta()**2 * (1 - exp(-self.mu() * self.timeDelta))**2)
        
        return output

    
    def sigma(self):
        
        output = self.var() * (2 * self.mu() / (1 - np.exp(-2 * self.mu() * self.timeDelta)))
        
        return output#sqrt(self.var())
    
    def parameter(self):
        
        return self.mu(), self.theta(), self.sigma()
    
if __name__ == "__main__":
    pass