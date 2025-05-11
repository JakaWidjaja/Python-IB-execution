from itertools import combinations

from UDF.PortfolioSelection import PortfolioSelection
from UDF.PortfolioWeightsOH import PortfolioWeightsOH

import warnings

class MeanRevertingPortfolio:
    def __init__(self, numTopStocks, lengthTimeSeries):
        self.numTopStocks     = numTopStocks      # Top stocks to use from PCA 
        self.lengthTimeSeries = lengthTimeSeries  # How many data to use
        self.portSelection = PortfolioSelection()
        self.portWeight = PortfolioWeightsOH()

    def StockSelection(self, data, numStockToUse, highLow):       
        '''
        data : pandas dataframe, first column date (asending). subsequent column stock names, consisting stock prices. 
        numStockToUse : The number of stock in each combination.
        highLow : indicator of whether to use high or low variance
        '''
        # Select the top stocks
        # Use PCA to select the highest or lowest variance
        topStocks = self.portSelection.PCA(data, self.lengthTimeSeries, self.numTopStocks, highLow)

        # Calculate the different stock combinations
        stockCombination = list(combinations(topStocks, numStockToUse))

        return stockCombination
    
    def PortfolioPositions(self, portfolioList, data, longShort):
        '''
        Parameters
        ----------
        portfolioList : list
            a list of combinations of stocks
        data : pandas dataframe
            pandas consisting of prices of the relevant stocks
        longShort : string
            indicator to do either short only or long only or long/short

        Returns
        -------
        positions : dictionary
            
        '''
        
        warnings.filterwarnings("ignore")
        
        # Calculate the weights and portfolio time series
        weights   = {}
        positions = {}

        for c in portfolioList:
            numStock = len(c)
            stockList = data.loc[:, c]
            weights[c] = self.portWeight.OH(stockList, self.lengthTimeSeries, [0.5] * numStock, longShort)
            '''
            weights[c] = self.portWeight.BoxTiao(stockList, 
                                   1,
                                   [0.5] * numStock, 
                                   longShort, 
                                   self.lengthTimeSeries)
            '''

            if sum(weights[c]) == 0:
                continue
            
            positions[c] = [c, weights[c]]
        
        return positions