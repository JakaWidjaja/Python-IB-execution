import numpy as np


class Autocovariance:
    '''
    Calculate the autocovariance matrix for a particular lag.
    '''
    def __init__(self, matrix, lag):
        '''
        Matrix argument is using numpy array
        lag is an integer. 
        '''
        self.matrix = matrix
        self.lag = lag
        
    def OutputMatrix(self):
        #Calculate the shapre of the matrix
        num_asset, num_data = np.shape(self.matrix)
        '''
        #normalised data. 
        ave = np.array([np.average(self.matrix[i,:]) for i in range (0,num_asset)])
        std = np.array([np.std(self.matrix[i,:]) for i in range(0, num_asset)])
        matrix_norm = np.array([(self.matrix[i, :] - ave[i]) / std[i] for i in range(0,num_asset)])
        '''
        #Lag matrix
        lag_matrix = self.matrix [:,self.lag:]
        
        #Initialised the autocovariance matrix
        autocovar = np.zeros((num_asset, num_asset))

        #Calculate the average
        ave_full = np.array([np.average(self.matrix [i,:]) for i in range(0,num_asset)])
        ave_lag =  np.array([np.average(self.matrix [i,self.lag:]) for i in range(0,num_asset)])
        
        #Subtract the data in the matrix and lag_matrix with the average
        matrix = self.matrix .transpose() - ave_full
        lag_matrix = lag_matrix.transpose() - ave_lag        
        
        #Calculate the autocovariance matrix
        for full_data in range(num_asset):
            for lag_data in range(num_asset):
                autocovar[full_data, lag_data] = \
                np.sum([matrix[:-self.lag, full_data] * lag_matrix[:, lag_data]]) * (1/(num_data - self.lag - 1))

        return autocovar
                
if __name__ == "__main__":
    pass