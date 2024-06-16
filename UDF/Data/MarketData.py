import time
import pandas as pd

class MarketData:
    def __init__(self):
        pass
    
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
        
        contractList = []
        for key, cont in self.contractDict.items():
            contractList.append(cont)
            
        for i, n in enumerate(contractList):
            self.tws.reqMktData(reqId              = i, 
                                contract           = n, 
                                genericTickList    = self.genericTickList, 
                                snapshot           = self.snapshot, 
                                regulatorySnapshot = self.regulatorySnapshot, 
                                mktDataOptions     = self.mktDataOptions)
        
        time.sleep(self.timeDelay)

    def SortMarketData(self, bid, ask, last, contractDictionary):
        self.bid                = bid
        self.ask                = ask
        self.last               = last
        self.contractDictionary = contractDictionary
        
        columnNames = ['ticker', 'bid', 'ask', 'mid', 'last']
        
        output = pd.DataFrame(columns = columnNames)
        for i, ticker in enumerate(contractDictionary):
            try:
                bidPrice  = bid[i]
            except:
                bidPrice = 0
                
            try:
                askPrice  = ask[i]
            except:
                askPrice = 0
                
            try: 
                lastPrice = last[i]
            except:
                lastPrice = 0
            
            midPrice = abs(askPrice - bidPrice)
            
            temp = pd.DataFrame([[ticker, bidPrice, askPrice, midPrice, lastPrice]], columns = columnNames)
            
            output = pd.concat([output, temp], ignore_index = True)
            
        return output