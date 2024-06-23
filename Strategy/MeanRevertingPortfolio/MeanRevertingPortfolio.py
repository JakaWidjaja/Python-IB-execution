from itertools import combinations

from UDF.Portfolio import PortfolioSelection, PortfolioWeights


class MeanRevertingPortfolio:
    def __init__(self):
        pass

    def StockSelection(self, data, lengthTimeSeries, numTopStocks, numStockToUse, longShort):
        self.data             = data
        self.lengthTimeSeries = lengthTimeSeries
        self.numTopStocks     = numTopStocks
        self.numStockToUse    = numStockToUse
        self.longShort        = longShort
        
        #Select the top stocks
        portSelection = PortfolioSelection.PortfolioSelection()
        topStocks = portSelection(self.data, self.lengthTimeSeries, self.numTopStocks)
        
        #Calculate the different stock combinations
        stockCombination = list(topStocks, self.numStockToUse)
        
        return stockCombination
        
        
    
    def EntryExit(self, portfolioList, data):
        self.portfolioList = portfolioList
        self.data          = data
        
        #Calculate the weights and portfolio time series
        weights = {}
        w = PortfolioWeights.PortfolioWeights()
        for c in self.portfolioList:
            stockList = data.loc[:, c]
            weights[c] = w.BoxTiao(stockList, 
                                   1,
                                   [0.5] * self.numStockToUse, 
                                   self.longShort, 
                                   self.lengthTimeSeries)
            
            sumProduct = stockList * weights[c]
            portfolioTimeSeries = sumProduct.sum(axis = 1)
        
        
        

            


