from itertools import combinations

from UDF.Portfolio import PortfolioSelection, PortfolioWeights


class MeanRevertingPortfolio:
    def __init__(self):
        pass

    def StockSelection(self, data, lengthTimeSeries, numTopStocks, numStockToUse):
        self.data             = data
        self.lengthTimeSeries = lengthTimeSeries
        self.numTopStocks     = numTopStocks
        self.numStockToUse    = numStockToUse
        
        #Select the top stocks
        portSelection = PortfolioSelection.PortfolioSelection()
        topStocks = portSelection(self.data, self.lengthTimeSeries, self.numTopStocks)
        
        #Calculate the different stock combinations
        stockCombination = list(topStocks, self.numStockToUse)