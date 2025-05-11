import time
import pandas as pd

class MarketData:
    reqIdCounter = 100
    
    def __init__(self):
        pass
    
    def TickStream(self, tws, contractDict):
        self.tws          = tws
        self.contractDict = contractDict
        
        for symbol, contract in contractDict.items():
            
            self.tws.reqIdToSymbol[MarketData.reqIdCounter] = symbol
            
            self.tws.reqTickByTickData(reqId         = MarketData.reqIdCounter, 
                                       contract      = contract, 
                                       tickType      = "AllLast", 
                                       numberOfTicks = 0,
                                       ignoreSize    = True)
            
            MarketData.reqIdCounter += 1  # Increment the global counter
    
    def GetMarketData(self, tws, contractDict, marketDataType, timeDelay, 
                      genericTickList = '', snapshot = False, regulatorySnapshot = False, mktDataOptions = []):
        self.tws                = tws
        self.contractDict       = contractDict
        self.marketDataType     = marketDataType
        self.timeDelay          = timeDelay
        self.genericTickList    = genericTickList
        self.snapshot           = snapshot
        self.regulatorySnapshot = regulatorySnapshot
        self.mktDataOptions     = mktDataOptions
        
        self.tws.reqMarketDataType(self.marketDataType)

        for symbol, contract in contractDict.items():
            # Store the mapping of reqId to the stock symbol in the twsWrapper object
            self.tws.reqIdToSymbol[MarketData.reqIdCounter] = symbol
            
            self.tws.reqMktData(reqId              = MarketData.reqIdCounter, 
                                contract           = contract, 
                                genericTickList    = self.genericTickList, 
                                snapshot           = self.snapshot, 
                                regulatorySnapshot = self.regulatorySnapshot, 
                                mktDataOptions     = self.mktDataOptions)

            MarketData.reqIdCounter += 1  # Increment the global counter
            
        time.sleep(self.timeDelay)
    
    def GetOptMktData(self, tws, contractDict, marketDataType, timeDelay, 
                      genericTickList = '', snapshot = False, regulatorySnapshot = False, mktDataOptions = []):
        self.tws                = tws
        self.contractDict       = contractDict
        self.marketDataType     = marketDataType
        self.timeDelay          = timeDelay
        self.genericTickList    = genericTickList
        self.snapshot           = snapshot
        self.regulatorySnapshot = regulatorySnapshot
        self.mktDataOptions     = mktDataOptions
        
        self.tws.reqMarketDataType(self.marketDataType)
        
        for symbol, contract in contractDict.items():
            # Store the mapping of reqId to the stock symbol in the twsWrapper object
            self.tws.reqIdToSymbol[MarketData.reqIdCounter] = symbol
            
            self.tws.reqMktData(reqId              = MarketData.reqIdCounter, 
                                contract           = contract, 
                                genericTickList    = self.genericTickList, 
                                snapshot           = self.snapshot, 
                                regulatorySnapshot = self.regulatorySnapshot, 
                                mktDataOptions     = self.mktDataOptions)

            MarketData.reqIdCounter += 1  # Increment the global counter
            
        time.sleep(self.timeDelay)

    def SortMarketData(self, bid, ask, last, contractDictionary):
        self.bid                = bid
        self.ask                = ask
        self.last               = last
        self.contractDictionary = contractDictionary
        
        columnNames = ['ticker', 'bid', 'ask', 'mid', 'last']
        output = pd.DataFrame(columns=columnNames)
    
        for ticker in self.contractDictionary.keys():
            bidPrice  = self.bid.get(ticker, 0)
            askPrice  = self.ask.get(ticker, 0)
            lastPrice = self.last.get(ticker, 0)
    
            # Calculate the mid price correctly
            midPrice = (askPrice + bidPrice) / 2 if askPrice > 0 and bidPrice > 0 else 0
    
            temp = pd.DataFrame([[ticker, bidPrice, askPrice, midPrice, lastPrice]], columns=columnNames)
            output = pd.concat([output, temp], ignore_index=True)
            
        return output
    
    def SortMktOptionData(self, contractDict, bid, ask, last, underlying, optionPrice, 
                          impVol, delta, gamma, vega, theta, div):
        self.contractDict = contractDict
        self.bid          = bid
        self.ask          = ask
        self.last         = last
        self.underlying   = underlying
        self.optionPrice  = optionPrice
        self.impVol       = impVol
        self.delta        = delta
        self.gamma        = gamma
        self.vega         = vega
        self.theta        = theta
        self.div          = div
        
        columnNames = ['ticker', 'bid', 'ask', 'mid', 'last', 'underlying', 'option price', 'imp vol',
                       'delta', 'gamma', 'vega', 'theta', 'dividend']
        output = pd.DataFrame(columns = columnNames)
        
        for ticker in self.contractDict.keys():
            tickName  = ticker
            bidPrice  = self.bid.get(ticker, 0)
            askPrice  = self.ask.get(ticker, 0)
            lastPrice = self.last.get(ticker, 0)
            impVol    = self.impVol[ticker]
            delta     = self.delta[ticker]
            gamma     = self.gamma[ticker]
            vega      = self.vega[ticker]
            theta     = self.theta[ticker]
            undPrice  = self.underlying[ticker]
            optPrice  = self.optionPrice[ticker]
            divPrice  = self.div[ticker]
            
            # Calculate the mid price correctly
            midPrice = (askPrice + bidPrice) / 2 if askPrice > 0 and bidPrice > 0 else 0
            
            temp = pd.DataFrame([[tickName, bidPrice, askPrice, midPrice, lastPrice, undPrice, optPrice,
                                  impVol, delta, gamma, vega, theta, divPrice]], columns = columnNames)
            
            output = pd.concat([output, temp], ignore_index = True)
            
        return output