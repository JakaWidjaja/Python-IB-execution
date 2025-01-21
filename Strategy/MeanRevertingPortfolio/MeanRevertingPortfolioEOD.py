from itertools import combinations

from UDF.Portfolio                   import PortfolioSelection, PortfolioWeights
from UDF.Utilities                   import ReScaleTimeSeries
from UDF.Models.OrnsteinUhlenbeck    import OrnsteinUhlenbeck 
from UDF.Models.OUHittingProbability import OUHittingProbability
from UDF.EntryExit                   import EntryExit
from UDF.Orders                      import Orders

import warnings

class MeanRevertingPortfolioEOD:
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
    
    def EntryExitSignal(self, portfolioList, data, longShort, lowPriceProb, highPriceProb):
        self.portfolioList = portfolioList
        self.data          = data
        self.longShort     = longShort
        self.lowPriceProb  = lowPriceProb
        self.highPriceProb = highPriceProb
        
        warnings.filterwarnings("ignore")
        
        #Initialised variable
        w       = PortfolioWeights.PortfolioWeights()
        reScale = ReScaleTimeSeries.ReScaleTimeSeries()
        oh      = OrnsteinUhlenbeck.OrnsteinUhlenbeck()
        highLow = OUHittingProbability.OUHittingProbability()
        entExt  = EntryExit.EntryExit()
        
        #Calculate the weights and portfolio time series
        weights       = {}
        positions     = {}
        count         = 1

        for c in self.portfolioList:
            stockList = data.loc[:, c]
            weights[c] = w.BoxTiao(stockList, 
                                   1,
                                   [0.5] * self.numStockToUse, 
                                   self.longShort, 
                                   self.lengthTimeSeries)
            
            if sum(weights[c]) == 0:
                continue
            
            sumProduct = stockList * weights[c]
            portfolioTimeSeries = sumProduct.sum(axis = 1)
        
            #Normalised the time series
            normTimeSeries = reScale.NormalisedNegativePositive(portfolioTimeSeries)
        
            mu, theta, sigma = oh.Moment(normTimeSeries)
            
            #Calibrate high and low price
            highPrice, lowPrice = highLow.CalibrateModel(mu, theta, sigma, normTimeSeries[-1], 
                                                         self.lowPriceProb, self.highPriceProb)
            
            highPriceUnScaled = reScale.NormalisedNegativePositiveReverse(portfolioTimeSeries, highPrice)
            lowPriceUnScaled = reScale.NormalisedNegativePositiveReverse(portfolioTimeSeries, lowPrice)
            
            positions[c] = [c, weights[c], highPriceUnScaled, lowPriceUnScaled, mu, theta, sigma]
            
            count += 1
        
        #sort positions
        positions = dict(sorted(positions.items(), key = lambda x:(x[1][5], x[1][6]), reverse = True))
        
        return positions
      
        
    def PortfolioTimeSeries(self, portfolios, marketData, portfolioTimeSeries):
        self.portfolios          = portfolios
        self.marketData          = marketData
        self.portfolioTimeSeries = portfolioTimeSeries
        
        for key, value in self.portfolios.items():
            stockCombinations = value[0]
            weights = value[1]
            
            portfolioPrice = 0
            for i, w in enumerate(weights):
                if w <= 0:
                    portfolioPrice += w * self.marketData.loc[self.marketData['ticker'] == stockCombinations[i], 'ask'].values[0]
                else:
                    portfolioPrice += w * self.marketData.loc[self.marketData['ticker'] == stockCombinations[i], 'bid'].values[0]
            
            self.portfolioTimeSeries[stockCombinations].append(portfolioPrice)
        
        return self.portfolioTimeSeries
    
    def PlaceOrder(self, tws, marketData, portfolios, portfolioTimeSeries, contractDict, activeTrading, 
                   orderObject):
        self.tws                 = tws
        self.marketData          = marketData
        self.portfolios          = portfolios
        self.portfolioTimeSeries = portfolioTimeSeries
        self.contractDict        = contractDict
        self.activeTrading       = activeTrading
        self.orderObject         = orderObject
        
        #Initialised variable
        entExt  = EntryExit.EntryExit()
        
        if self.activeTrading: #if active
            return self.activeTrading, 0, 0, 'none'
        else:
            stockDict = {}
            direction = []
            quantity  = []
            
            for key, value in self.portfolioTimeSeries.items():
                stockCombinations = key
                timeSeries        = value
                weights           = self.portfolios[stockCombinations][1]
                lowPrice          = self.portfolios[stockCombinations][2]
                highPrice         = self.portfolios[stockCombinations][3]

                if entExt.EntryRisingPrice(timeSeries, lowPrice) == 'Enter Long':
                    #Get the cash amount from portfolio
                    self.tws.reqAccountValue()
                    accountValues = self.tws.dfAccountValues
                    cash = float(accountValues.loc[accountValues['tag'] == 'CashBalance', 'value'].values[0])
                    
                    #Cash amount per stocks
                    cashAmountPerStocks = (abs(weights) * cash).astype(int)
                    
                    #identify the quantity and direction
                    for i, n in enumerate(stockCombinations):
                        bidPrice = self.marketData.loc[self.marketData['ticker'] == n, 'bid'].values[0]
                        askPrice = self.marketData.loc[self.marketData['ticker'] == n, 'ask'].values[0]
                        
                        stockDict[n] = self.contractDict[n]
                        if weights[i] < 0:
                            quantity.append(cashAmountPerStocks[i] / bidPrice)
                            direction.append('SELL')
                        elif weights[i] > 0:
                            quantity.append(cashAmountPerStocks[i] / askPrice)
                            direction.append('BUY')
                            
                    self.orderObject.MultiMktOrder(stockDict, direction, quantity)
                
                    return True, lowPrice, highPrice, 'long' #Active 
            return False, 0, 0, direction #Not active and no signal to be active. 
                 
        
    def LiquidationOrder(self, portfolio, contractDict, orderObject):
        self.portfolio    = portfolio
        self.contractDict = contractDict
        self.orderObject  = orderObject
        
        stockDict = {}
        position  = []
        direction = []
        for i in range(len(self.portfolio)):
            tickerName     = self.portfolio.iloc[i, self.portfolio.columns.get_loc('symbol')]
            tickerPosition = self.portfolio.iloc[i, self.portfolio.columns.get_loc('position')]
            stockDict[i]   = self.contractDict[tickerName]
            
            position.append(tickerPosition)
            if tickerPosition < 0:
                direction.append('SELL')
            else:
                direction.append('BUY')
                
        orderObject.MultiMktOrder(stockDict, direction, position)
        

