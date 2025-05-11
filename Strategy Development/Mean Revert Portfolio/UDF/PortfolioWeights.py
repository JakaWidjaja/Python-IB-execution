from UDF.Autocovariance import Autocovariance
    
import numpy as np
from scipy.optimize import minimize

class PortfolioWeights(object):
    
    def __init__(self):
        pass
    
    def BoxTiao(self, data, lag, weights, longShort, numData): 
        '''
        minimising the Box-Tiao predictability 
        '''
        #Stock names
        stockNames = list(data.columns)
        
        #Convert dataframe to list
        timeSeries = np.array([data[col].tail(numData).tolist() for col in stockNames])

        numStock, series = np.shape(timeSeries)
        
        #Calculate the autocovariance
        covarFull = np.cov(timeSeries)
        
        #Calculate the lag autocovariance
        initCovarLag = Autocovariance(timeSeries, lag)
        covarLag = initCovarLag.OutputMatrix()
        
        #Create a function to minimise
        def func(w):
            w = w / timeSeries[0:numStock, -1]
            
            #Calculate M
            m = np.matmul(np.matmul(covarLag, covarFull), covarLag.transpose())
            
            return np.matmul(np.matmul(w.transpose(), m), w) * 1e8
        
        #Initiate the minimisation function
        init = weights
        
        #Set the constraints        
        const = ({'type':'eq', 'fun' : lambda x: 0.99 - sum(x)} )
        
        #Set the boundary
        if longShort == 'longshort':
            bnds = [(-0.99, 0.99)] * len(weights)
        elif longShort == 'long':
            bnds = [(0.0, 0.99)] * len(weights)
        elif longShort == 'short':
            bnds = [(-0.99, 0.0)] * len(weights)
            
        #minimise the function and calculate the weights
        res = minimize(func, init, method='trust-constr', bounds= bnds, constraints = const)  
        if res.success == True and sum(res.x) == 0.99:
            return res.x
        
        res = minimize(func, init, method='Nelder-Mead', bounds= bnds, constraints = const)  
        if res.success == True and sum(res.x) == 0.99:
            return res.x
        
        res = minimize(func, init, method='Powell', bounds= bnds, constraints = const)  
        if res.success == True and sum(res.x) == 0.99:
            return res.x
        
        res = minimize(func, init, method='CG', bounds= bnds, constraints = const)  
        if res.success == True and sum(res.x) == 0.99:
            return res.x
        
        res = minimize(func, init, method='BFGS', bounds= bnds, constraints = const)  
        if res.success == True and sum(res.x) == 0.99:
            return res.x
        
        res = minimize(func, init, method='L-BFGS-B', bounds= bnds, constraints = const)  
        if res.success == True and sum(res.x) == 0.99:
            return res.x
        
        res = minimize(func, init, method='TNC', bounds= bnds, constraints = const)  
        if res.success == True and sum(res.x) == 0.99:
            return res.x

        return [0.0] * len(weights)
    
    
        
        
if __name__ == '__main__':
    pass


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    