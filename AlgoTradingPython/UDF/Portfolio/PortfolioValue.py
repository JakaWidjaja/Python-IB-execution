
class PortfolioValue:
    def __init__(self):
        pass
    
    def Value(self, portfolio, marketData):
        self.portfolio = portfolio
        self.marketData = marketData
        
        portfolioValue = 0
        
        for i in range(len(self.portfolio)):
            tickerName = self.portfolio.iloc[i, self.portfolio.columns.get_loc('symbol')]
            tickerPosition = self.portfolio.iloc[i, self.portfolio.columns.get_loc('position')]
            
            if tickerPosition < 0:
                tickerPrice = self.marketData.loc[self.marketData['ticker'] == tickerName, 'bid'].values[0]
            else:
                tickerPrice = self.marketData.loc[self.marketData['ticker'] == tickerName, 'ask'].values[0]
                
            portfolioValue += tickerPosition * tickerPrice
            
        return portfolioValue           