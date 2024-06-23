import numpy as np

class MethodMoment:
    '''
    Ornstein Uhlenbeck model. 
    Calibrated using Method of Moment
    '''
    
    def __init__(self, timeSeries):
        '''
        time_series: an array of time series. 
        '''
        self.timeSeries = np.array(timeSeries)
        self.n = len(self.timeSeries) #the number of data in the time series. 
        
    def m1(self):
        
        return sum(self.timeSeries) / (self.n + 1.0)
    
    def m2(self):
        
        return 1.0 / self.n * sum((self.timeSeries - self.m1()) ** 2)
    
    def m3(self):
        
        return 1.0 / (self.n-1) * sum((self.timeSeries[1:self.n] - self.m1()) * 
                      (self.timeSeries[0:(self.n-1)] - self.m1()))

    def theta(self):
        
        return self.n * np.log(self.m2() / self.m3())
    
    def mu(self):
        
        return self.m1()
    
    def variance(self):
        #if self.m2() < self.m3():
            #return 2 * self.n * self.m2() * np.log(self.m3() / self.m2())
        #else:
        return 2 * self.n * self.m2() * np.log(self.m2() / self.m3())
    
    def sigma(self):
        
        return np.sqrt(self.variance())

    def parameter(self):
        
        return self.mu(), self.theta(), self.sigma()

if __name__ == '__main__':
    pass