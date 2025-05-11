import pandas as pd
import numpy  as np
import copy
from scipy.signal import savgol_filter

from UDF.Models.OrnsteinUhlenbeck import OrnsteinUhlenbeck
from Strategy.MeanRevertingPortfolio import TrendSignal, MeanRevertSignal

class GenerateSignals:
    def __init__(self, config, indicators, stockCombinations, money):   
        self.stockCombinations = stockCombinations
        self.money             = money
        
        self.hurstExp  = indicators['hurst']
        self.vRatio    = indicators['vr']
        self.hlife     = indicators['hl']        # Half-Life
        self.doubleSMA = indicators['doubleSMA']
        
        self.oh = OrnsteinUhlenbeck.OrnsteinUhlenbeck()
        
        # Strategy
        self.trending = TrendSignal.TrendSignal(config)
        self.meanRevert = MeanRevertSignal.MeanRevertSignal(config)
        
        # Container
        self.trendStrategy = pd.DataFrame()
        self.meanRevertStrategy = pd.DataFrame()
        
    def Signals(self, data):
        for key, value in self.stockCombinations.items():
            stockNames = list(value[0])
            weights    = value[1]
            
            # Portfolio data
            portfolioData = copy.deepcopy(data[stockNames])
            
            # Calculate the number of stock
            dollarAllocation = self.money * weights
            prices = portfolioData.iloc[-1].replace(0, np.nan)
            numberOfShares = np.trunc(dollarAllocation / prices).fillna(0).astype(int)
            
            # Combine time series and smooth
            portfolioData['total'] = portfolioData.dot(numberOfShares.values)
            portfolioData['total smooth'] = savgol_filter(portfolioData['total'], window_length = 30, polyorder = 10)
            
            # Indicators
            hurst = self.hurstExp.Calculate(list(portfolioData['total smooth']))
            vr    = self.vRatio.Calculate(list(portfolioData['total smooth']))
            hl    = self.hlife.Calculate(list(portfolioData['total smooth']))
            
            # Ornstein-Uhlenbeck
            mu, theta, sigma = self.oh.Moment(list(portfolioData['total smooth']))
            
            # Double SMA
            longShortSignal = self.doubleSMA.Calculate(portfolioData)
            
            # Last Price
            lastPrice = portfolioData['total'].iloc[-1]
           
            ###########################################################################################     
            # Trending
            trendingStrategy = self.trending.Signal(hurst, vr, hl, longShortSignal, lastPrice, stockNames, portfolioData)
            if not trendingStrategy.empty:
                self.trendStrategy = pd.concat([self.trendStrategy, trendingStrategy], ignore_index = True)
                
            ###########################################################################################    
  
            ###########################################################################################     
            # Mean Reverting
            meanRevertStrategy = self.meanRevert.Signal(hurst, hl, longShortSignal, mu, sigma, lastPrice, stockNames, portfolioData)
            if not meanRevertStrategy.empty:
                self.meanRevertStrategy = pd.concat([self.meanRevertStrategy , meanRevertStrategy], ignore_index = True)
            ###########################################################################################    
        
        return self.meanRevertStrategy, self.trendStrategy   