#TWS library
from ibapi.contract import Contract

#UDF
from UDF.Contract import EquityContract
from UDF.Contract import FXContract
from UDF.Contract import OptionContract
from UDF.Contract import FuturesContract

import pandas as pd

class MakeContract:
    def __init__(self):
        pass
        
    def contractObjectList(self, productList):        
        #initiate specific contract object
        equity  = EquityContract.EquityContract()
        fx      = FXContract.FXContract()
        option  = OptionContract.OptionContract()
        futures = FuturesContract.FuturesContract()
        
        contractMap = {} #Storage
        for i in range(len(productList)):
            twsContract = Contract()
            
            #get the contract type, e.g., Stock, FX, Futures, Option, etc
            contractType = productList.iloc[i, productList.columns.get_loc('Type')]  
            
            if contractType == 'Stock':
                symbol   = productList.iloc[i, productList.columns.get_loc('Symbol')]   
                secType  = productList.iloc[i, productList.columns.get_loc('SecType')]
                currency = productList.iloc[i, productList.columns.get_loc('Currency')]
                exchange = productList.iloc[i, productList.columns.get_loc('Exchange')]
                
                contractMap[symbol] = equity.contract(twsContract, symbol, secType, currency, exchange)
            elif contractType == 'FX':
                symbol   = productList.iloc[i, productList.columns.get_loc('Symbol')]   
                secType  = productList.iloc[i, productList.columns.get_loc('SecType')]
                currency = productList.iloc[i, productList.columns.get_loc('Currency')]
                exchange = productList.iloc[i, productList.columns.get_loc('Exchange')]
                
                contractMap[symbol] = fx.contract(twsContract, symbol, secType, currency, exchange)
            elif contractType == 'Option':
                symbol                       = productList.iloc[i, productList.columns.get_loc('Symbol')]
                secType                      = productList.iloc[i, productList.columns.get_loc('SecType')]
                currency                     = productList.iloc[i, productList.columns.get_loc('Currency')]
                exchange                     = productList.iloc[i, productList.columns.get_loc('Exchange')]
                right                        = productList.iloc[i, productList.columns.get_loc('Right')]
                strike                       = productList.iloc[i, productList.columns.get_loc('Strike')]
                multiplier                   = productList.iloc[i, productList.columns.get_loc('Multiplier')]
                lastTradeDateOrContractMonth = productList.iloc[i, productList.columns.get_loc('LastTradeDateOrContractMonth')]
                
                tickName = symbol + str(lastTradeDateOrContractMonth) + right + str(strike)
                contractMap[tickName] = option.contract(twsContract, symbol, secType, currency, exchange, 
                                                      right, strike, lastTradeDateOrContractMonth, 
                                                      multiplier)
            elif contractType == 'Futures':
                symbol                       = productList.iloc[i, productList.columns.get_loc('Symbol')]
                secType                      = productList.iloc[i, productList.columns.get_loc('SecType')]
                currency                     = productList.iloc[i, productList.columns.get_loc('Currency')]
                exchange                     = productList.iloc[i, productList.columns.get_loc('Exchange')]
                multiplier                   = productList.iloc[i, productList.columns.get_loc('Multiplier')]
                lastTradeDateOrContractMonth = productList.iloc[i, productList.columns.get_loc('LastTradeDateOrContractMonth')]
                
                tickName = symbol  + str(lastTradeDateOrContractMonth)#+ str(lastTradeDateOrContractMonth)
                contractMap[tickName] = futures.contract(twsContract, symbol, secType, currency, exchange, 
                                                         str(lastTradeDateOrContractMonth), multiplier)

        return contractMap
                
