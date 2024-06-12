from ibapi.client   import EClient
from ibapi.wrapper  import EWrapper
from ibapi.ticktype import TickTypeEnum

import threading
import time
import pandas as pd

class twsWrapper(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.histData = {}
        
        self.mktDataBid = {}
        self.mktDataAsk = {}
        self.mktDataLast = {}
        
        self.dfPosition = pd.DataFrame(columns=['account' , 'symbol'  , 'sec type',
                                                'currency', 'position', 'ave cost'])
        
    def Login(self, host, port, clientId, sleepTime):
        self.host      = host
        self.port      = port
        self.clientId  = clientId
        self.sleepTime = sleepTime
        
        self.connect(self.host, self.port, self.clientId)
        
        connThread = threading.Thread(target = self.run, daemon = True)
        connThread.start()
        
        #Allow sometime to establish connection
        time.sleep(self.sleepTime)
        
    def historicalData(self, reqId, bar):
        self.reqId = reqId
        self.bar   = bar
        
        if self.reqId not in self.data:
            self.histData[self.reqId] = pd.DataFrame([{'date'   : self.bar.date, 
                                                       'open'   : self.bar.open, 
                                                       'high'   : self.bar.high, 
                                                       'low'    : self.bar.low, 
                                                       'close'  : self.bar.close, 
                                                       'volume' : self.bar.volume}])
        else:
            self.histData[self.reqId] = pd.concat((self.histData[self.reqId], 
                                                   pd.DataFrame([{'date'   : self.bar.date, 
                                                                  'open'   : self.bar.open, 
                                                                  'high'   : self.bar.high, 
                                                                  'low'    : self.bar.low, 
                                                                  'close'  : self.bar.close, 
                                                                  'volume' : self.bar.volume}])))
        
    def tickPrice(self, reqId, tickType, price, attrib):
        self.reqId    = reqId
        self.tickType = tickType
        self.price    = price
        self.attrib   = attrib
        
        super().tickPrice(self.reqId, self.tickType, self.price, self.attrib)
        #print(TickTypeEnum.to_str(self.tickType), self.price)

        if TickTypeEnum.to_str(self.tickType) == 'DELAYED_LAST' or TickTypeEnum.to_str(self.tickType) =='LAST':
            self.mktDataLast[reqId] = self.price
        if TickTypeEnum.to_str(self.tickType) == 'DELAYED_BID' or TickTypeEnum.to_str(self.tickType) =='BID':
            self.mktDataBid[self.reqId] = price
        if TickTypeEnum.to_str(self.tickType) == 'DELAYED_ASK' or TickTypeEnum.to_str(self.tickType) =='ASK':
            self.mktDataBid[self.reqId] = price
            
    def nextValidId(self, orderId):
        super().nextValidId(orderId)
        self.nextValidOrderId = orderId
        
    def position(self, account, contract, position, avgCost):
        self.account  = account
        self.contract = contract
        self.position = position
        self.avgCost  = avgCost
        
        super().position(account, contract, position, avgCost)
        
        mapping = {'account'  : self.account, 
                   'symbol'   : self.contract.symbol, 
                   'sec type' : self.contract.secType, 
                   'currency' : self.contract.currency, 
                   'position' : self.position, 
                   'ave cost' : self.avgCost}
        
        if self.dfPosition['symbol'].str.contains(self.contract.symbol).any():
            self.dfPosition.loc[self.dfPosition['symbol'] == self.contract.symbol, 'position'] = self.position
            self.dfPosition.loc[self.dfPosition['symbol'] == self.contract.symbol, 'ave cost'] = self.avgCost
        else:
            self.dfPosition = pd.concat((self.dfPosition, pd.DataFrame([mapping])), ignore_index = True)


        