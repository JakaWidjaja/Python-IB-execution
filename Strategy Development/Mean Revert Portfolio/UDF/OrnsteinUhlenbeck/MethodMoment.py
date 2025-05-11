import numpy as np

class MethodMoment:
    '''
    Ornstein Uhlenbeck model. 
    Calibrated using Method of Moment
    '''
    
    def __init__(self, timeSeries):
        self.timeSeries = np.array(timeSeries)
        self.n = len(self.timeSeries)
        self.mean = np.mean(self.timeSeries)
        self.var = np.var(self.timeSeries, ddof=1)
        self.autocov = np.sum((self.timeSeries[1:] - self.mean) * 
                              (self.timeSeries[:-1] - self.mean)) / (self.n - 1)

    def theta(self):
        rho = self.autocov / self.var
        if rho <= 0:
            raise ValueError("Autocorrelation is non-positive, cannot take log.")
        return -np.log(rho)

    def mu(self):
        return self.mean

    def variance(self):
        return 2 * self.theta() * self.var

    def sigma(self):
        return np.sqrt(self.variance())

    def parameter(self):
        return self.mu(), self.theta(), self.sigma()

if __name__ == '__main__':
    pass