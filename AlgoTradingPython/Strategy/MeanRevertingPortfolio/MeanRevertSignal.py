import pandas as pd

class MeanRevertSignal:
    def __init__(self, config):
        self.stopLossPerc1 = config.loc[config['name'] == 'stop loss 1' , 'value'].values[0]
        self.stopLossPerc2 = config.loc[config['name'] == 'stop loss 2' , 'value'].values[0]
        self.profitLimit   = config.loc[config['name'] == 'profit limit', 'value'].values[0]
    
    def Signal(self, hurst, hl, doubleSMA, mu, sigma, lastPrice, stockNames, portfolioData):
        strategy = pd.DataFrame()
        
        if hurst < 0.40 and hl > 0.0 and hl < 100.0:
            # Short
            if ((lastPrice > mu) and (doubleSMA['sma short'].iloc[-1] > (mu + sigma))) or \
               ((lastPrice > mu) and (doubleSMA['sma short'].iloc[-1] < (mu - sigma))):
                   strategy = pd.DataFrame([{'direction'           : 'short',
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
                   
            elif ((lastPrice < mu) and (doubleSMA['sma short'].iloc[-1] < (mu - sigma))) or \
                 ((lastPrice < mu) and (doubleSMA['sma short'].iloc[-1] > (mu + sigma))):
                     strategy = pd.DataFrame([{'direction'           : 'long',
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
        return strategy
    
        