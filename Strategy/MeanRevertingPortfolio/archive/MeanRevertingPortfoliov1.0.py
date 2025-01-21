from itertools import combinations

from UDF.Portfolio                import PortfolioSelection, PortfolioWeights
from UDF.Utilities                import ReScaleTimeSeries
from UDF.Models.OrnsteinUhlenbeck import OrnsteinUhlenbeck 
from UDF.Models.BertramEntryExit  import BertramEntryExit
from UDF.EntryExit                import EntryExit
from UDF.Orders                   import Orders

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
        self.longShort     = longShort
        
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
            
            
            highPriceUnScaled = reScale.NormalisedNegativePositiveReverse(portfolioTimeSeries, highPrice)
            lowPriceUnScaled = reScale.NormalisedNegativePositiveReverse(portfolioTimeSeries, lowPrice)
            
            #Check whether there is trading opportunity
            if entExt.EntryRisingPrice(normTimeSeries, lowPrice) == 'Enter Long':
                longPosition[longCount] = [c, weights[c], highPriceUnScaled, lowPriceUnScaled]
                longCount += 1
            
            if entExt.EntryFallingPrice(normTimeSeries, highPrice) == 'Enter Short':
                shortPosition[shortCount] = [c, weights[c] * -1, highPriceUnScaled, lowPriceUnScaled]
                shortCount += 1
                
            return longPosition, shortPosition
      
    def PlaceOrder(self, signalGeneration, bidPrices, askPrices, midPrices, 
                   numberOfStocksToSelect, tws, orderObject, contractDict, activeTrading):
        self.signalGeneration       = signalGeneration
        self.bidPrices              = bidPrices
        self.askPrices              = askPrices
        self.midPrices              = midPrices
        self.numberOfStocksToSelect = numberOfStocksToSelect
        self.tws                    = tws
        self.orderObject            = orderObject
        self.contractDict           = contractDict
        self.activeTrading          = activeTrading #boolean to determine if currently active
        
        if self.activeTrading: #if active
            return self.activeTrading, 0, 0, 'none'
        else: #if not active
            stockDict = {}
            direction = []
            quantity  = []
            direction ='none'
            
            #Create a list of stocks combinations
            stockCombinations = self.signalGeneration.StockSelection(self.midPrices, 
                                                                     self.numberOfStocksToSelect)
            
            #Create long/short portfolio 
            longOrder, shortOrder = self.signalGeneration.EntryExitSignal(stockCombinations, self.midPrices, 
                                                                          'longshort')
            
            #Check if there are opportunities to enter into a trade
            if longOrder:
                stocks     = longOrder[1][0]
                weights    = longOrder[1][1] #numpy array
                entryPrice = longOrder[1][2]
                exitPrice  = longOrder[1][3]
                self.activeTrading = True
                
            elif shortOrder:
                stocks     = shortOrder[1][0]
                weights    = shortOrder[1][1]
                entryPrice = shortOrder[1][3]
                exitPrice  = shortOrder[1][2]
                self.activeTrading = True
                
            if self.activeTrading:
                #Get the cash amount from portfolio
                self.tws.reqAccountValue()
                accountValues = self.tws.dfAccountValues
                cash = float(accountValues.loc[accountValues['tag'] == 'CashBalance', 'value'].values[0])
                
                #Cash amount per stocks
                cashAmountPerStocks = (abs(weights) * cash).astype(int)
                
                #Set-up variables for placing order
                for i, n in enumerate(stocks):
                    stockDict[n] = self.contractDict[n]
                    if weights[i] < 0:
                        quantity.append(cashAmountPerStocks[i] / self.bidPrices.iloc[-1, self.bidPrices.columns.get_loc(n)])
                        direction.append('SELL')
                    elif weights[i] > 0:
                        quantity.append(cashAmountPerStocks[i] / self.bidPrices.iloc[-1, self.askPrices.columns.get_loc(n)])
                        direction.append('BUY')
                        
                orderObject.MultiMktOrder(stockDict, direction, quantity)
                
                if entryPrice < exitPrice:
                    direction = 'long'
                elif entryPrice > exitPrice:
                    direction = 'short'
                else:
                    direction = 'none'
                
                return True, entryPrice, exitPrice, direction #Active 
                
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
        

