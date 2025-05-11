import pandas as pd
import numpy  as np
from scipy.signal import savgol_filter

from UDF.OrnsteinUhlenbeck import OrnsteinUhlenbeck

class BacktestingOutSample:
    def __init__(self, data, config, signal, indicators, dataCountLimit = -1):
        self.data      = data
        self.signal    = signal
        self.hurstExp  = indicators['hurst']
        self.vRatio    = indicators['vr']
        self.hlife     = indicators['hl'] # Half-Life
        self.doubleSMA = indicators['doubleSMA']
        self.dataCountLimit = dataCountLimit
        
        self.numCalibrationData = config['numCalibrationData']
        self.numStocks          = config['numStocks']
        self.stopLossPerc1      = config['stopLossPerc1']
        self.stopLossPerc2      = config['stopLossPerc2']
        self.profitLimit        = config['profitLimit']
        
        self.storageTrend = pd.DataFrame()
        self.storageRevert = pd.DataFrame()
        
        self.oh = OrnsteinUhlenbeck.OrnsteinUhlenbeck()
        
        self.money = 1000
        
    def Backtest(self):
        countLoop = 0
        
        for i in range(len(self.data) - self.numCalibrationData):
            if self.dataCountLimit == -1:
                pass # Out Sample data
            elif countLoop > self.dataCountLimit:
                break # In Sample data
            
            history = self.data[i : (i + self.numCalibrationData)]
            
            portCombinations = self.signal.StockSelection(history.iloc[:, 1:], self.numStocks, 'low')
            portWeight = self.signal.PortfolioPositions(portCombinations, history, 'long')
            
            date = history['date'].iloc[-1]
            print(date)
            
            for key, value in portWeight.items():
                stockNames = list(value[0])
                weights    = value[1]

                stockNames = ['date'] + stockNames
                
                histData = history[stockNames].copy()

                # Calculate the number of stock
                dollarAllocation = self.money * weights
                prices = histData.iloc[-1].iloc[1:] # Skip the date column 
                numberOfShares = dollarAllocation / prices
                numberOfShares = np.trunc(numberOfShares).astype(int)
                print(numberOfShares)
                print(numberOfShares.index[0], numberOfShares.index[1], numberOfShares.index[2])
                print(numberOfShares[0], numberOfShares[1], numberOfShares[2])
                histData['total'] = histData.iloc[:, 1:].dot(numberOfShares)
                histData['total smooth'] = savgol_filter(histData['total'], window_length = 30, polyorder = 10)
                
                # Future time series
                futureTS = self.data.loc[self.data['date'] > date, stockNames].copy()
                futureTS['total'] = futureTS.iloc[:, 1:].dot(numberOfShares)
                
                # Indicator
                hurst = self.hurstExp.Calculate(list(histData['total smooth']))
                vr = self.vRatio.Calculate(list(histData['total smooth']))
                hl = self.hlife.Calculate(list(histData['total smooth']))
                
                # Ornstein-Uhlenbeck
                mu, theta, sigma = self.oh.Moment(list(histData['total smooth']))
                
                # Double SMA
                longShortSignal = self.doubleSMA.Calculate(histData)
                
                # Last Price
                lastPrice = histData['total'].iloc[-1]
                
                ###########################################################################################     
                ###########################################################################################     
                # Trending
                buy = sell = pnl = 0.0
                direction = ''
                if hurst >= 0.55 and vr > 1.0 and hl < 0.0:
                    if abs(longShortSignal['sma short'].iloc[-1] - longShortSignal['sma long'].iloc[-1]) < 1.0:
                        continue
                    elif longShortSignal['sma short'].iloc[-1] > longShortSignal['sma long'].iloc[-1]:
                        buy        = histData['total'].iloc[-1]
                        stopLoss   = buy * (1 - self.stopLossPerc1)
                        priceLimit = buy * (1 + self.profitLimit)
                        direction  = 'long'
                    else:
                        sell       = histData['total'].iloc[-1]
                        stopLoss   = sell * (1 + self.stopLossPerc1)
                        priceLimit = sell * (1 - self.profitLimit)
                        direction  = 'short'
                        
                    for n in range(len(futureTS)):
                        price = futureTS['total'].iloc[n]
                        
                        if direction == 'long':
                            stopLoss = max(stopLoss, price * (1 - self.stopLossPerc2) if price >= priceLimit else price * (1 - self.stopLossPerc1))
                        elif direction == 'short':
                            stopLoss = min(stopLoss, price * (1 + self.stopLossPerc2) if price <= priceLimit else price * (1 + self.stopLossPerc1))
                            
                        exitTrigger = (direction == 'long' and price <= stopLoss) or (direction =='short' and price >= stopLoss)
                        if exitTrigger:
                            exitPrice = price
                            
                            if direction == 'long':
                                pnl = exitPrice - buy
                                sell = exitPrice
                            elif direction == 'short':
                                pnl = sell - exitPrice
                                buy = exitPrice

                            self.storageTrend = pd.concat([self.storageTrend, 
                                                      pd.DataFrame([{'date'      : date, 
                                                                     'info'      : value, 
                                                                     'history'   : histData[['date', 'total', 'total smooth']], 
                                                                     'future'    : futureTS[['date', 'total']], 
                                                                     'hurst'     : hurst, 
                                                                     'vr'        : vr, 
                                                                     'hl'        : hl, 
                                                                     'last price' : lastPrice,
                                                                     'mu'         : mu, 
                                                                     'theta'      : theta, 
                                                                     'sigma'      : sigma,
                                                                     'direction' : direction, 
                                                                     'buy'       : buy,
                                                                     'sell'      : sell, 
                                                                     'pnl'       : pnl
                                                          }])], ignore_index = True)
                            
                            # Reset
                            buy = sell = pnl = 0.0
                            direction = ''
                            
                ###########################################################################################    
                ###########################################################################################     
                # Mean Reverting
                buy = sell = pnl = 0.0
                direction = ''
                if hurst < 0.40 and hl > 0.0 and hl < 100.0:
                    # Short
                    if ((lastPrice > mu) and (longShortSignal['sma short'].iloc[-1] > (mu + sigma))) or \
                       ((lastPrice > mu) and (longShortSignal['sma short'].iloc[-1] < (mu - sigma))):
                        sell       = histData['total'].iloc[-1]
                        stopLoss   = sell * (1 + self.stopLossPerc1)
                        priceLimit = sell * (1 - self.profitLimit)
                        direction  = 'short'
                    
                    elif ((lastPrice < mu) and (longShortSignal['sma short'].iloc[-1] < (mu - sigma))) or \
                         ((lastPrice < mu) and (longShortSignal['sma short'].iloc[-1] > (mu + sigma))):
                           buy        = histData['total'].iloc[-1]
                           stopLoss   = buy * (1 - self.stopLossPerc1)
                           priceLimit = buy * (1 + self.profitLimit)
                           direction  = 'long'
                        
                    for n in range(len(futureTS)):
                        price = futureTS['total'].iloc[n]
                        
                        if direction == 'long':
                            stopLoss = max(stopLoss, price * (1 - self.stopLossPerc2) if price >= priceLimit else price * (1 - self.stopLossPerc1))
                        elif direction == 'short':
                            stopLoss = min(stopLoss, price * (1 + self.stopLossPerc2) if price <= priceLimit else price * (1 + self.stopLossPerc1))
                            
                        exitTrigger = (direction == 'long' and price <= stopLoss) or (direction =='short' and price >= stopLoss)
                        if exitTrigger:
                            exitPrice = price
                            
                            if direction == 'long':
                                pnl = exitPrice - buy
                                sell = exitPrice
                            elif direction == 'short':
                                pnl = sell - exitPrice
                                buy = exitPrice

                            self.storageRevert = pd.concat([self.storageRevert, 
                                                      pd.DataFrame([{'date'      : date, 
                                                                     'info'      : value, 
                                                                     'history'   : histData[['date', 'total', 'total smooth']], 
                                                                     'future'    : futureTS[['date', 'total']], 
                                                                     'hurst'     : hurst, 
                                                                     'vr'        : vr, 
                                                                     'hl'        : hl, 
                                                                     'last price' : lastPrice,
                                                                     'mu'         : mu, 
                                                                     'theta'      : theta, 
                                                                     'sigma'      : sigma,
                                                                     'direction' : direction, 
                                                                     'buy'       : buy,
                                                                     'sell'      : sell, 
                                                                     'pnl'       : pnl
                                                          }])], ignore_index = True)
                            
                            # Reset
                            buy = sell = pnl = 0.0
                            direction = ''
            countLoop += 1               
        return self.storageTrend, self.storageRevert