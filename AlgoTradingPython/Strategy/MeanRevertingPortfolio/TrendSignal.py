import pandas as pd

class TrendSignal:
    def __init__(self, config):
        self.stopLossPerc1 = config.loc[config['name'] == 'stop loss 1' , 'value'].values[0]
        self.stopLossPerc2 = config.loc[config['name'] == 'stop loss 2' , 'value'].values[0]
        self.profitLimit   = config.loc[config['name'] == 'profit limit', 'value'].values[0]
    
    def Signal(self, hurst, vr, hl, doubleSMA, lastPrice, stockNames, portfolioData):
        if hurst >= 0.55 and vr > 1.0 and hl < 0.0:
            if abs(doubleSMA['sma short'].iloc[-1] - doubleSMA['sma long'].iloc[-1]) < 1.0:
                return pd.DataFrame()
            
            if doubleSMA['sma short'].iloc[-1] > doubleSMA['sma long'].iloc[-1]:
                direction = 'long'
            else:
                direction = 'short'
            
            
            if direction == 'long':
                stopLossMult = 1 - self.stopLossPerc1
            else:
                stopLossMult = 1 + self.stopLossPerc1
            
            
            strategyDict = {'direction' : direction,
                            'portfolio value' : lastPrice, 
                            'portfolio stop loss' : lastPrice * stopLossMult}
            
            for i, name in enumerate(stockNames):
                strategyDict[f'stock {i + 1} name'] = name
                strategyDict[f'stock {i + 1} name shares'] = stockNames.index[i]
                strategyDict[f'stock {i + 1} stop loss'] = portfolioData[name].iloc[-1] * stopLossMult
                
            return pd.DataFrame([strategyDict])