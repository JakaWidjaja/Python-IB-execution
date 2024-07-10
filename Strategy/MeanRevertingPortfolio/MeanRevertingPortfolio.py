from itertools import combinations

from UDF.Portfolio import PortfolioSelection, PortfolioWeights
from UDF.Utilities import ReScaleTimeSeries
from UDF.Models.OrnsteinUhlenbeck import OrnsteinUhlenbeck 

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
        
        #Initialised variable
        reScale = ReScaleTimeSeries.ReScaleTimeSeries()
        oh      = OrnsteinUhlenbeck.OrnsteinUhlenbeck()
        
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
        
            #Normalised the time series
            normTimeSeries = reScale.Normalised(portfolioTimeSeries)
        
            mu, theta, sigma = oh.Moment(normTimeSeries)
            


