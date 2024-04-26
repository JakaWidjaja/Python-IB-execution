import sys
sys.path.insert(0, '/home/lun/Desktop/Folder 2/Python/model/ornstein uhlenbeck')
sys.path.insert(0, '/home/lun/Desktop/Folder 2/Python/model/autocovariance')
from ornstein_uhlenbeck import oh_model
from autocovariance import autocovariance
    
import numpy as np
from scipy.optimize import minimize, fmin

np_exp = np.exp
np_sum = np.sum
np_log = np.log
np_transpose = np.transpose
np_norm = np.linalg.norm
np_matmul = np.matmul
np_cov = np.cov

class portfolio(object):
    
    def __init__(self):
        pass
    
    def box_tiao(self, timeSeries, lag, weights, longShort):
        self.timeSeries = timeSeries
        self.lag        = lag
        self.weights    = weights
        self.longShort  = longShort
        '''
        minimising the Box-Tiao predictability 
        '''
        numStock, series = np.shape(self.timeSeries)
        
        #Calculate the autocovariance
        covarFull = np_cov(self.timeSeries)
        
        #Calculate the lag autocovariance
        initCovarLag = autocovariance(self.timeSeries, self.lag)
        covarLag = initCovarLag.output_matrix()
        
        #Create a function to minimise
        def func(w):
            w = w / self.timeSeries[0:numStock, -1]
            
            #Calculate M
            m = np.matmul(np.matmul(covarLag, covarFull), covarLag.transpose())
            
            return np_matmul(np_matmul(w.transpose(), m), w) #* 1e8
        
        #Initiate the minimisation function
        init = self.weights
        
        #Set the constraints        
        const = ({'type':'eq', 'fun' : lambda x: 0.99 - sum(x)} )
        
        #Set the boundary
        if self.longShort == 'longshort':
            bnds = [(-0.99, 0.99)] * len(self.weights)
        elif self.longShort == 'long':
            bnds = [(0.0, 0.99)] * len(self.weights)
        elif self.longShort == 'short':
            bnds = [(-0.99, 0.0)] * len(self.weights)
            
        #minimise the function and calculate the weights
        res = minimize(func, init, method='SLSQP', bounds= bnds, constraints= const)  
        
        return res.x
    
    
        
        
if __name__ == '__main__':
    weights = np.array([0.3,0.25,0.85])
    lag = 1
    
    port = portfolio()
    weights = port.box_tiao(time_series, lag, weights)
    weights
    
    port_time_series = np.sum(np.transpose(time_series) * weights, axis = 1)
    plt.plot(port_time_series)

    mean_revert_model = oh_model(port_time_series) #Initialised model
    mu, theta, sigma = mean_revert_model.method_of_moment()
    mu
    theta
    sigma
    
    mean_revert_model = oh_model(port_time_series) #Initialised model
    mu, theta, sigma = mean_revert_model.max_likelihood()
    mu
    theta
    sigma
    
    mean_revert_model = oh_model(price_track_1[start:end]) #Initialised model
    mu, theta, sigma = mean_revert_model.method_of_moment()
    mu
    theta
    sigma


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    