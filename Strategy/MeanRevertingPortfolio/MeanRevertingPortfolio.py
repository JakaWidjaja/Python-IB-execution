from itertools import combinations

from UDF.Portfolio import PortfolioSelection, PortfolioWeights
from UDF.Utilities import ReScaleTimeSeries
from UDF.Models.OrnsteinUhlenbeck import OrnsteinUhlenbeck 
from UDF.Models.BertramEntryExit  import BertramEntryExit
from UDF.EntryExit import EntryExit

import warnings

class MeanRevertingPortfolio:
    def __init__(self, numStockToUse, lengthTimeSeries):
        self.numStockToUse    = numStockToUse
        self.lengthTimeSeries = lengthTimeSeries

    def StockSelection(self, data, numTopStocks):
        self.data             = data
        self.numTopStocks     = numTopStocks
        
        #Select the top stocks
        #Use PCA to select the highest variance
        portSelection = PortfolioSelection.PortfolioSelection()
        topStocks = portSelection.PCA(self.data, self.lengthTimeSeries, self.numTopStocks)

        #Calculate the different stock combinations
        stockCombination = list(combinations(topStocks, self.numStockToUse))

        return stockCombination
        
        
    
    def EntryExitSignal(self, portfolioList, data, longShort):
        self.portfolioList = portfolioList
        self.data          = data
        self.longShort        = longShort
        
        warnings.filterwarnings("ignore")
        
        #Initialised variable
        w       = PortfolioWeights.PortfolioWeights()
        reScale = ReScaleTimeSeries.ReScaleTimeSeries()
        oh      = OrnsteinUhlenbeck.OrnsteinUhlenbeck()
        highLow = BertramEntryExit.BertramEntryExit()
        entExt  = EntryExit.EntryExit()
        
        #Calculate the weights and portfolio time series
        weights       = {}
        longPosition  = {}
        shortPosition = {}
        longCount     = 1
        shortCount    = 1
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
            normTimeSeries = reScale.NormalisedNegativePositive(portfolioTimeSeries)
        
            mu, theta, sigma = oh.Moment(normTimeSeries)
            
            #Calibrate high and low price
            highPrice, lowPrice = highLow.CalibrateModel(0.0005, 
                                                         max(normTimeSeries), 
                                                         min(normTimeSeries), mu, theta, sigma)
            
            #Check whether there is trading opportunity
            if entExt.EntryRisingPrice(normTimeSeries, lowPrice) == 'Enter Long':
                longPosition[longCount] = [c, weights[c], highPrice, lowPrice]
                longCount += 1
            
            if entExt.EntryFallingPrice(normTimeSeries, highPrice) == 'Enter Short':
                shortPosition[shortCount] = [c, weights[c] * -1, highPrice, lowPrice]
                shortCount += 1
                
            return longPosition, shortPosition