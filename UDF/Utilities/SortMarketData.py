import pandas as pd

class SortMarketData:
    def __init__(self):
        pass
    
    def SortBidAskMid(self, newData, dfBid, dfAsk, dfMid):
        self.newData = newData
        self.dfBid   = dfBid
        self.dfAsk   = dfAsk
        self.dfMid   = dfMid
        
        bid = self.newData[['ticker', 'bid']].set_index('ticker').T
        ask = self.newData[['ticker', 'ask']].set_index('ticker').T
        mid = self.newData[['ticker', 'mid']].set_index('ticker').T
        
        bidTimeSeries = pd.concat([self.dfBid, bid])
        askTimeSeries = pd.concat([self.dfAsk, ask])
        midTimeSeries = pd.concat([self.dfMid, mid])
        
        return bidTimeSeries, askTimeSeries, midTimeSeries
        
