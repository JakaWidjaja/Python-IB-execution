from ibapi.client   import EClient
from ibapi.wrapper  import EWrapper
from ibapi.ticktype import TickTypeEnum

import threading
import time
import pandas as pd

class twsWrapper(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.histData         = {}
        self.histDataComplete = {}
        
        self.mktDataBid  = {}
        self.mktDataAsk  = {}
        self.mktDataLast = {}
        self.mktUndPrice = {}
        self.mktOptPrice = {}
        self.mktImpVol   = {}
        self.mktDelta    = {}
        self.mktGamma    = {}
        self.mktVega     = {}
        self.mktTheta    = {}
        self.mktPvDiv    = {}
        # Initialize the reverse lookup dictionary
        self.reqIdToSymbol = {}
        
        self.dfPosition = pd.DataFrame(columns=['account' , 'symbol'  , 'sec type',
                                                'currency', 'position', 'ave cost'])
        
        self.dfAccountValues = pd.DataFrame(columns=['account', 'tag', 'value', 'currency'])
        self.reqId = 0
        
        self.tickData = pd.DataFrame(columns = ['symbol', 'price', 'size', 'time', 'exchange', 'specialCond'])
        
    def tickByTickAllLast(self, reqId, tickType, time, price, size, attribs, exchange, specialConditions):
        
        symbol = self.reqIdToSymbol.get(reqId, "Unknown Symbol")
        if symbol != "Unknown Symbol":
            newRow = pd.DataFrame([{'symbol'            : symbol, 
                                    'price'             : price, 
                                    'size'              : size, 
                                    'time'              : time, 
                                    'exchange'          : exchange, 
                                    'specialConditions' : specialConditions}])
            
            self.tickData = pd.concat([self.tickData, newRow], ignore_index = True)
    
    def getNextReqId(self):
        self.reqId += 1
        return self.reqId
    
    def Login(self, host, port, clientId, sleepTime):        
        self.connect(host, port, clientId)
        
        connThread = threading.Thread(target = self.run, daemon = True)
        connThread.start()
        
        #Allow sometime to establish connection
        time.sleep(sleepTime)
        
    def error(self, reqId, errorCode, errorMsg):
        print(f"❗ IB ERROR | reqId={reqId} | code={errorCode} | msg={errorMsg}")
        
    def historicalData(self, reqId, bar):        
        newRow = pd.DataFrame([{
        'date': bar.date,
        'open': bar.open,
        'high': bar.high,
        'low': bar.low,
        'close': bar.close,
        'volume': bar.volume
        }])
    
        if reqId not in self.histData or isinstance(self.histData[reqId], list):
            self.histData[reqId] = newRow
        else:
            self.histData[reqId] = pd.concat([self.histData[reqId], newRow], ignore_index=True)
            
    def historicalDataEnd(self, reqId, start, end):
        print(f"Historical data complete for reqId={reqId}")
        if reqId in self.histDataComplete:
            self.histDataComplete[reqId].set()
        
    def tickPrice(self, reqId, tickType, price, attrib):
        
        super().tickPrice(reqId, tickType, price, attrib)
        
        # Get the stock symbol using the reqId
        symbol = self.reqIdToSymbol.get(reqId, "Unknown Symbol")
        
        if symbol != "Unknown Symbol":
            if TickTypeEnum.to_str(tickType) == 'DELAYED_LAST' or TickTypeEnum.to_str(tickType) =='LAST':
                self.mktDataLast[symbol] = price
            if TickTypeEnum.to_str(tickType) == 'DELAYED_BID' or TickTypeEnum.to_str(tickType) =='BID':
                self.mktDataBid[symbol] = price
            if TickTypeEnum.to_str(tickType) == 'DELAYED_ASK' or TickTypeEnum.to_str(tickType) =='ASK':
                self.mktDataAsk[symbol] = price

    def tickOptionComputation(self, reqId, tickType, impliedVol, delta, optPrice, pvDividend, gamma, vega, 
                              theta, undPrice):
        
        symbol = self.reqIdToSymbol.get(reqId, 'unknown Symbol')
        if symbol != "Unknown Symbol":
            self.mktImpVol[symbol]   = impliedVol
            self.mktDelta[symbol]    = delta
            self.mktGamma[symbol]    = gamma
            self.mktVega[symbol]     = vega
            self.mktTheta[symbol]    = theta
            self.mktUndPrice[symbol] = undPrice
            self.mktOptPrice[symbol] = optPrice
            self.mktPvDiv[symbol]    = pvDividend

    def requestImpliedVolatility(self, contract):
        self.contract = contract
        
        reqId = self.getNextReqId()
        self.reqIdToSymbol[reqId] = contract.symbol
        self.reqMktData(reqId, contract, "", False, False, [])
 
    def nextValidId(self, orderId):
        super().nextValidId(orderId)
        self.nextValidOrderId = orderId
        
    def position(self, account, contract, position, avgCost):        
        super().position(account, contract, position, avgCost)
        
        mapping = {'account'  : account, 
                   'symbol'   : contract.symbol, 
                   'sec type' : contract.secType, 
                   'currency' : contract.currency, 
                   'position' : position, 
                   'ave cost' : avgCost}
        
        if self.dfPosition['symbol'].str.contains(contract.symbol).any():
            self.dfPosition.loc[self.dfPosition['symbol'] == contract.symbol, 'position'] = position
            self.dfPosition.loc[self.dfPosition['symbol'] == contract.symbol, 'ave cost'] = avgCost
        else:
            self.dfPosition = pd.concat((self.dfPosition, pd.DataFrame([mapping])), ignore_index = True)

    def reqAccountValue(self):
        reqId = self.getNextReqId()
        self.reqAccountSummary(reqId, "All", "$LEDGER")

    def accountSummary(self, reqId, account, tag, value, currency):
        super().accountSummary(reqId, account, tag, value, currency)

        mapping = {'account': account, 'tag': tag, 'value': value, 'currency': currency}

        if ((self.dfAccountValues['account'] == account) & (self.dfAccountValues['tag'] == tag) & 
            (self.dfAccountValues['currency'] == currency)).any():
            self.dfAccountValues.loc[(self.dfAccountValues['account'] == account) &
                                     (self.dfAccountValues['tag'] == tag) &
                                     (self.dfAccountValues['currency'] == currency), 'value'] = value
        else:
            self.dfAccountValues = pd.concat((self.dfAccountValues, pd.DataFrame([mapping])), ignore_index=True)

    def accountSummaryEnd(self, reqId):
        super().accountSummaryEnd(reqId)
        self.cancelAccountSummary(reqId)
        
        
        