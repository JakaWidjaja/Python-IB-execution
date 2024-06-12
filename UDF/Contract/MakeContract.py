#TWS library
from ibapi.contract import Contract

#UDF
from UDF.Contract import EquityContract
from UDF.Contract import FXContract

import pandas as pd

class MakeContract:
    def __init__(self):
        pass
        
    def contractObjectList(self, productListPath):
        self.productListPath = productListPath
        
        #initiate specific contract object
        equity = EquityContract.EquityContract()
        fx     = FXContract.FXContract()
        
        #Get product list
        productList = pd.read_csv(self.productListPath)
        
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
                
                
        return contractMap
                
        