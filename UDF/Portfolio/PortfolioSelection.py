from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

import numpy as np
import pandas as pd

class PortfolioSelection:
    def __init__(self):
        pass
    
    def PCA(self, data, numData, numStocks, highLow):
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
        highLow : string
            select whether to use the highest variance or lowest variance

        Returns
        -------
        list of stock tickers
        '''
        
        #Stock Names
        stockList = list(data.columns[:])
        
        #Get the prices only, ignore the date column
        #Calculate the daily return and remove na
        dfData = data.iloc[:,:].tail(numData).pct_change().dropna()
        dfData = dfData.replace([np.inf, -np.inf], np.nan).dropna(axis = 0)
        
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
        if highLow.lower() == 'high':
            topStocks = eigenVectors.abs().sum(axis = 1).nlargest(numStocks).index
        else:
            topStocks = eigenVectors.abs().sum(axis = 1).nsmallest(numStocks).index

        return list(topStocks)