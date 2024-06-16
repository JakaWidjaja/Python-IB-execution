from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

import numpy as np
import pandas as pd

class PortfolioSelection:
    def __init__(self):
        pass
    
    def PCA(self, data, numData, numStocks):
        '''
        Parameters
        ----------
        data : Pandas DataFrame
            Dataframe of stock prices.
            First column is the date sorted from old to new
            Corresponding Columns are the prices of the different stocks
        numData: int
            How many historical dates points to use
        numStocks : int
            The number of stock to choose. i.e. the top numStocks that has the highest variance contribution. 

        Returns
        -------
        list of stock tickers
        '''
        self.data      = data
        self.numData   = numData
        self.numStocks = numStocks #The number of stocks to select
        
        #Stock Names
        stockList = list(self.data.columns[1:])
        
        #Get the prices only, ignore the date column
        #Calculate the daily return and remove na
        dfData = self.data.iloc[:, 1:].tail(self.numData).pct_change().dropna()
        
        #Standardised the returns
        scaler = StandardScaler()
        standardised = scaler.fit_transform(dfData)
        
        #Calculate PCA
        pca = PCA()
        pca.fit(standardised)
        
        #Calculate the variance ratio
        explainVarRatio = pca.explained_variance_ratio_
        cummVarRatio = np.cumsum(explainVarRatio)
        
        #Eigenvectors
        eigenVectors = pd.DataFrame(pca.components_.T, columns=[f'PC{i+1}' for i in range(len(cummVarRatio))], 
                                    index = stockList)
        
        #Select the top x stocks
        topStocks = eigenVectors.abs().sum(axis = 1).nlargest(self.numStocks).index
        
        return list(topStocks)
        



















