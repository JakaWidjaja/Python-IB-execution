import numpy as np
from scipy.optimize import minimize
from scipy.signal import savgol_filter

from UDF.OrnsteinUhlenbeck import OrnsteinUhlenbeck

class PortfolioWeightsOH:
    def __init__(self):
        
        self.oh = OrnsteinUhlenbeck.OrnsteinUhlenbeck()
    
    def OH(self, data, numData, weights, longShort):
        
        #Stock names
        stockNames = list(data.columns)
        
        #Convert dataframe to list
        timeSeries = data[stockNames].tail(numData).to_numpy() 
        
        numStock, series = np.shape(timeSeries)
        
        def objective(w):
            weightedSeries = timeSeries @ w
            
            weightedSeries = savgol_filter(weightedSeries, window_length = 30, polyorder = 10)
        
            mu, theta, sigma = self.oh.Moment(list(weightedSeries))
            
            return - (theta - sigma)
        
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
            
        res = minimize(objective, init, method = 'SLSQP', bounds = bnds, constraints = const)
        
        return res.x
    
if __name__ == '__main__':
    stockName = ['APH', 'BAC', 'BKR']
    
    d = data[['APH', 'BAC', 'BKR']]
    numData = 250
    weights = [0.5, 0.5, 0.5]

    p = PortfolioWeights('longshort')
    p.OH(d, numData, weights)
