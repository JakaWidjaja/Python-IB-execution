from UDF.Utilities import Autocovariance
    
import numpy as np
from scipy.optimize import minimize, fmin

class PortfolioWeights(object):
    
    def __init__(self):
        pass
    
    def BoxTiao(self, data, lag, weights, longShort, numData): 
        self.data      = data
        self.lag       = lag
        self.weights   = weights
        self.longShort = longShort
        self.numData   = numData
        '''
        minimising the Box-Tiao predictability 
        '''
        #Stock names
        stockNames = list(self.data.columns)
        
        #Convert dataframe to list
        timeSeries = np.array([self.data[col].tail(self.numData).tolist() for col in stockNames])

        numStock, series = np.shape(timeSeries)
        
        #Calculate the autocovariance
        covarFull = np.cov(timeSeries)
        
        #Calculate the lag autocovariance
        initCovarLag = Autocovariance.Autocovariance(timeSeries, self.lag)
        covarLag = initCovarLag.OutputMatrix()
        
        #Create a function to minimise
        def func(w):
            w = w / timeSeries[0:numStock, -1]
            
            #Calculate M
            m = np.matmul(np.matmul(covarLag, covarFull), covarLag.transpose())
            
            return np.matmul(np.matmul(w.transpose(), m), w) * 1e8
        
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
        
        return res.x#dict(zip(stockNames, res.x))
    
    
        
        
if __name__ == '__main__':
    pass


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    