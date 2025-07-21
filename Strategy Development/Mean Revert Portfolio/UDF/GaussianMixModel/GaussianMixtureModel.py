import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture

class GaussianMixtureModel:
    def __init__(self, numClusters = 2, covarianceType = 'full', randomState = None):
        self.numClusters = numClusters
        self.covarianceType = covarianceType
        self.randomState = randomState
        self.model = None
        self.fitted = None
    
    def Fit(self, timeSeries):
        
        if not isinstance(timeSeries, pd.Series):
            raise ValueError('Input time series must be a pandas series.')
            
        timeSeries = timeSeries.dropna().values.reshape(-1, 1)
        self.model = GaussianMixture(n_components = self.numClusters, 
                                     covariance_type = self.covarianceType, 
                                     random_state = self.randomState)
        
        self.model.fit(timeSeries)
        self.fitted = True
        
    def Params(self):
        if not self.fitted:
            raise RuntimeError("Model must be fitted first before calling Params")
            
        means = self.model.means_.flatten()
        stds = np.sqrt(self.model.covariances_.flatten())
        weights = self.model.weights_
        
        return means, stds, weights
    
    def PredictLabels(self, timeSeries):
        if not self.fitted:
            raise RuntimeError("Model must be fitted first before calling PredictLabels")
            
        return self.model.predict(timeSeries.values. reshape(-1, 1))
    
    def PredictProbs(self, timeSeries):
        if not self.fitted:
            raise RuntimeError("Model must be fitted first before calling PredictLabels")
            
        return self.model.predict_proba(timeSeries.values.reshape(-1, 1))