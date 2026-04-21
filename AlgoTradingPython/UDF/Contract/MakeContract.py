#TWS library
from ibapi.contract import Contract, ComboLeg

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
                tradingClass                 = productList.iloc[i, productList.columns.get_loc('TradingClass')]
                
                tickName = symbol + str(lastTradeDateOrContractMonth) + right + str(strike)
                contractMap[tickName] = option.contract(twsContract, symbol, secType, currency, exchange, 
                                                      right, strike, lastTradeDateOrContractMonth, tradingClass,
                                                      multiplier)
            elif contractType == 'Futures':
                symbol                       = productList.iloc[i, productList.columns.get_loc('Symbol')]
                secType                      = productList.iloc[i, productList.columns.get_loc('SecType')]
                currency                     = productList.iloc[i, productList.columns.get_loc('Currency')]
                exchange                     = productList.iloc[i, productList.columns.get_loc('Exchange')]
                multiplier                   = productList.iloc[i, productList.columns.get_loc('Multiplier')]
                lastTradeDateOrContractMonth = productList.iloc[i, productList.columns.get_loc('LastTradeDateOrContractMonth')]
                tradingClass                 = productList.iloc[i, productList.columns.get_loc('TradingClass')]
                localSymbol                  = productList.iloc[i, productList.columns.get_loc('LocalSymbol')]

                if pd.notna(lastTradeDateOrContractMonth):
                    tickName = symbol + str(lastTradeDateOrContractMonth)
                else:
                    tickName = localSymbol
                contractMap[tickName] = futures.contract(twsContract, secType, currency, exchange, symbol,
                                                         lastTradeDateOrContractMonth, multiplier, 
                                                         tradingClass, localSymbol)


        return contractMap
    
    def MakeButterflyContract(self, contractDict, symbol, currency, exchange = 'CME'):
        '''
        Build an IB Combo (BAG) contract for a butterfly.
        contractDict keys look like: 'long put 1', 'short put 1', 'short put 2', 'long put 2'
        '''
    
        def leg(conId, amount, action):
            l = ComboLeg()
            l.conId    = int(conId)
            l.ratio    = int(amount)
            l.action   = action
            l.exchange = exchange
            return l
    
        bag = Contract()
        bag.symbol   = symbol
        bag.secType  = 'BAG'
        bag.currency = currency
        bag.exchange = exchange
    
        # compress duplicate contracts (e.g., short put 1 and short put 2 are same conId)
        conIdCount  = {}
        conIdAction = {}
    
        for key, cont in contractDict.items():
            direction, _, _ = key.split(' ')  # 'long put 1'
            action = 'BUY' if direction == 'long' else 'SELL'
    
            cid = int(cont.conId)
            conIdCount[cid]  = conIdCount.get(cid, 0) + 1
            conIdAction[cid] = action
    
        legs = []
        for cid, count in conIdCount.items():
            legs.append(leg(cid, count, conIdAction[cid]))
    
        bag.comboLegs = legs
        return bag
        
        
                
