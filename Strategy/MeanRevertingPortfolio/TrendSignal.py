import pandas as pd

class TrendSignal:
    def __init__(self, config):
        self.stopLossPerc1 = config.loc[config['name'] == 'stop loss 1' , 'value'].values[0]
        self.stopLossPerc2 = config.loc[config['name'] == 'stop loss 2' , 'value'].values[0]
        self.profitLimit   = config.loc[config['name'] == 'profit limit', 'value'].values[0]
    
    def Signal(self, hurst, vr, hl, doubleSMA, lastPrice, stockNames, portfolioData):
        if hurst >= 0.55 and vr > 1.0 and hl < 0.0:
            if abs(doubleSMA['sma short'].iloc[-1] - doubleSMA['sma long'].iloc[-1]) < 1.0:
                pass
            elif doubleSMA['sma short'].iloc[-1] > doubleSMA['sma long'].iloc[-1]:
                # Long
                trendingStrategy = pd.DataFrame([{'direction'           : 'long',
                                      'stock 1 name'        : stockNames[0], 
                                      'stock 2 name'        : stockNames[1], 
                                      'stock 3 name'        : stockNames[2], 
                                      'stock 1 num shares'  : stockNames.index[0],
                                      'stock 2 num shares'  : stockNames.index[1],
                                      'stock 3 num shares'  : stockNames.index[2],
                                      'portfolio value'     : lastPrice, 
                                      'stock 1 stop loss'   : portfolioData[stockNames[0]].iloc[-1] * (1 - self.stopLossPerc1),
                                      'stock 2 stop loss'   : portfolioData[stockNames[1]].iloc[-1] * (1 - self.stopLossPerc1),
                                      'stock 3 stop loss'   : portfolioData[stockNames[2]].iloc[-1] * (1 - self.stopLossPerc1),
                                      'portfolio stop loss' : lastPrice * (1 - self.stopLossPerc1)
                                      }])
            else:
                # Short
                trendingStrategy = pd.DataFrame([{'direction'           : 'short',
                                      'stock 1 name'        : stockNames[0], 
                                      'stock 2 name'        : stockNames[1], 
                                      'stock 3 name'        : stockNames[2], 
                                      'stock 1 num shares'  : stockNames.index[0],
                                      'stock 2 num shares'  : stockNames.index[1],
                                      'stock 3 num shares'  : stockNames.index[2],
                                      'portfolio value'     : lastPrice, 
                                      'stock 1 stop loss'   : portfolioData[stockNames[0]].iloc[-1] * (1 + self.stopLossPerc1),
                                      'stock 2 stop loss'   : portfolioData[stockNames[1]].iloc[-1] * (1 + self.stopLossPerc1),
                                      'stock 3 stop loss'   : portfolioData[stockNames[2]].iloc[-1] * (1 + self.stopLossPerc1),
                                      'portfolio stop loss' : lastPrice * (1 + self.stopLossPerc1)
                                      }])
            return trendingStrategy
        
        else:
            return pd.DataFrame()