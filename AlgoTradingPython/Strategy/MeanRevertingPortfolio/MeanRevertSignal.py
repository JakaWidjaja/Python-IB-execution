import pandas as pd

class MeanRevertSignal:
    def __init__(self, config):
        self.stopLossPerc1 = config.loc[config['name'] == 'stop loss 1'          , 'value'].values[0]
        self.stopLossPerc2 = config.loc[config['name'] == 'stop loss 2'          , 'value'].values[0]
        self.profitLimit   = config.loc[config['name'] == 'profit limit'         , 'value'].values[0]
        self.hurstLevel    = config.loc[config['name'] == 'hurst level'          , 'value'].values[0]
        self.hlLowerLimit  = config.loc[config['name'] == 'Half-life lower limit', 'value'].values[0]
        self.hlUpperLimit  = config.loc[config['name'] == 'Half-life lower limit', 'value'].values[0]
        self.SMAMult       = config.loc[config['name'] == 'SMA Multiplication'   , 'value'].values[0]
    
    def Signal(self, hurst, hl, doubleSMA, mu, sigma, lastPrice, stockNames, portfolioData):
        strategy = pd.DataFrame()
        
        if hurst < self.hurstLevel  and hl > self.hlLowerLimit and hl < self.hlUpperLimit:
            stopLossMult = 1- self.stopLossPerc1
            
            
            # Short
            if ((lastPrice > mu) and (doubleSMA['sma short'].iloc[-1] > (mu + sigma * self.SMAMult))) or \
               ((lastPrice > mu) and (doubleSMA['sma short'].iloc[-1] < (mu - sigma * self.SMAMult))):
                   
                   strategyDict = {'direction' : 'short', 
                                   'portfolio value' : lastPrice,
                                   'portfolio stop loss' : lastPrice * stopLossMult}
                   
                   for i, name in enumerate(stockNames):
                       strategyDict[f'stock {i + 1} name'] = name
                       strategyDict[f'stock {i + 1} num shares'] = stockNames.index[i]
                       strategyDict[f'stock {i + 1} stop loss'] = portfolioData[name].iloc[-1] * stopLossMult
                       
                   strategy = pd.DataFrame([strategyDict])
                   
            #Long
            elif ((lastPrice < mu and doubleSMA['sma short'].iloc[-1] < (mu - sigma * self.SMAMult)) or
                  (lastPrice < mu and doubleSMA['sma short'].iloc[-1] > (mu + sigma * self.SMAMult))):
                
                strategyDict = {'direction' : 'long', 
                                'portfolio value' : lastPrice,
                                'portfolio stop loss' : lastPrice * stopLossMult}
                
                for i, name in enumerate(stockNames):
                    strategyDict[f'stock {i + 1} name'] = name
                    strategyDict[f'stock {i + 1} num shares'] = stockNames.index[i]
                    strategyDict[f'stock {i + 1} stop loss'] = portfolioData[name].iloc[-1] * stopLossMult
                
                strategy = pd.DataFrame([strategyDict])
                
        return strategy