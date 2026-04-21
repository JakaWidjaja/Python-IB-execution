from ibapi.client   import EClient
from ibapi.wrapper  import EWrapper
from ibapi.ticktype import TickTypeEnum

import threading
import time
import pandas as pd

class twsWrapper(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.connectedEvent = threading.Event()
        
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
        
        # Account summary sync
        self.accountSummaryEndEvent = {}
        self.accountUpdateEndEvent  = threading.Event()
        
        # Orders
        self.orderIdEvent = threading.Event()
        
        # Contracts
        self.contractDetailsData     = {}
        self.contractDetailsEndEvent = {}
        self.contractDetailsLock     = threading.Lock()
        
        # Initialize the reverse lookup dictionary
        self.reqIdToSymbol = {}
        
        # Event tick prices
        self.eventLast   = {}
        self.eventBidAsk = {}
        
        # Options
        self.secDefOptParams         = {}
        self.secDefOptParamsComplete = {}
        self.secDefLock              = threading.Lock()
        
        self.dfPosition = pd.DataFrame(columns=['account' , 'symbol'  , 'sec type',
                                                'currency', 'position', 'ave cost'])
        
        self.dfAccountValues = pd.DataFrame(columns=['account', 'tag', 'value', 'currency'])
        self.reqId = 50000
        
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
    
    def Login(self, host, port, clientId, timeout=10):   
        self.connectedEvent.clear()
        self.orderIdEvent.clear()
        
        self.connect(host, port, clientId)
        
        connThread = threading.Thread(target = self.run, daemon = True)
        connThread.start()
        
        if not self.connectedEvent.wait(timeout):
            raise RuntimeError("IB connection failed (no nextValidId)")
        
    def error(self, reqId, errorCode, errorMsg):
        print(f"❗ IB ERROR | reqId={reqId} | code={errorCode} | msg={errorMsg}")

        # If a contractDetails request fails (e.g., error 200),
        # contractDetailsEnd will NOT arrive → unblock any waiter.
        if errorCode == 200:
            ev = self.contractDetailsEndEvent.get(reqId)
            if ev is not None:
                ev.set()
        
    def historicalData(self, reqId, bar):        
        newRow = pd.DataFrame([{
        'date'  : bar.date,
        'open'  : bar.open,
        'high'  : bar.high,
        'low'   : bar.low,
        'close' : bar.close,
        'volume': bar.volume
        }])
    
        if reqId not in self.histData or self.histData[reqId] is None:
            self.histData[reqId] = newRow
        else:
            self.histData[reqId] = pd.concat([self.histData[reqId], newRow],
                                             ignore_index=True)
            
    def historicalDataEnd(self, reqId, start, end):
        print(f"Historical data complete for reqId={reqId}")
        if reqId in self.histDataComplete:
            self.histDataComplete[reqId].set()
        
    def tickPrice(self, reqId, tickType, price, attrib):
        symbol = self.reqIdToSymbol.get(reqId)
        if symbol is None:
            return
    
        # BID / DELAYED_BID
        if tickType in (1, 66):
            self.mktDataBid[symbol] = price
    
        # ASK / DELAYED_ASK
        elif tickType in (2, 67):
            self.mktDataAsk[symbol] = price
    
        # LAST / DELAYED_LAST
        elif tickType in (4, 68):
            self.mktDataLast[symbol] = price
            evt = self.eventLast.get(symbol)
            if evt is not None and price and price > 0:
                evt.set()
    
        # bid/ask event (set only when both sides are valid)
        b = float(self.mktDataBid.get(symbol, 0.0) or 0.0)
        a = float(self.mktDataAsk.get(symbol, 0.0) or 0.0)

        if b > 0.0 and a > 0.0 and a >= b:
            evt = self.eventBidAsk.get(symbol)
            if evt is not None and not evt.is_set():
                evt.set()
        

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
        self.connectedEvent.set()
        self.orderIdEvent.set() 
        
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

    def reqAccountValue(self, tags="$LEDGER", timeout=2.0):
        reqId = self.getNextReqId()

        ev = threading.Event()
        if not hasattr(self, "accountSummaryEndEvent"):
            self.accountSummaryEndEvent = {}
        self.accountSummaryEndEvent[reqId] = ev
    
        self.reqAccountSummary(reqId, "All", tags)
    
        ev.wait(timeout)
        return reqId

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
    
        ev = None
        try:
            ev = self.accountSummaryEndEvent.get(reqId)
        except Exception:
            ev = None
        if ev is not None:
            ev.set()
        
    def contractDetails(self, reqId, contractDetails):
        with self.contractDetailsLock:
            self.contractDetailsData.setdefault(reqId, []).append(contractDetails)


    def contractDetailsEnd(self, reqId):
        ev = self.contractDetailsEndEvent.get(reqId)
        if ev:
            ev.set() 
            
    def securityDefinitionOptionParameter(self, reqId, exchange, underlyingConId,
                                      tradingClass, multiplier, expirations, strikes):
        row = {"exchange"        : exchange,
               "underlyingConId" : underlyingConId,
               "tradingClass"    : tradingClass,
               "multiplier"      : multiplier,
               "expirations"     : set(expirations),
               "strikes"         : set(strikes)}
        
        with self.secDefLock:
            self.secDefOptParams.setdefault(reqId, []).append(row)
    
    
    def securityDefinitionOptionParameterEnd(self, reqId):
        # IB signals all rows delivered
        ev = self.secDefOptParamsComplete.get(reqId)
        if ev is not None:
            ev.set()
    
    def qualifyContracts(self, contractDict, timeout=5.0):
        """
        Qualify a dict of IB Contract objects by populating conId via reqContractDetails.
    
        contractDict: {"call_7050": Contract(...), ...}
        Returns: same dict (contracts updated in-place) and a list of keys that failed.
        """
    
        failed = []
    
        for key, c in contractDict.items():
            # already qualified
            if int(getattr(c, "conId", 0) or 0) > 0:
                continue
    
            reqId = self.getNextReqId()
    
            # prepare event + storage
            self.contractDetailsEndEvent[reqId] = threading.Event()
            with self.contractDetailsLock:
                self.contractDetailsData[reqId] = []
    
            # request details
            self.reqContractDetails(reqId, c)
    
            # wait
            if not self.contractDetailsEndEvent[reqId].wait(timeout):
                failed.append(key)
                continue
    
            # read response
            with self.contractDetailsLock:
                rows = self.contractDetailsData.get(reqId, [])
    
            if not rows:
                failed.append(key)
                continue
    
            # take first match (usually one)
            cd = rows[0]
            qualified = cd.contract
    
            # IMPORTANT: set conId back onto original object
            c.conId = qualified.conId
    
        return contractDict, failed
    
    def openOrder(self, orderId, contract, order, orderState):
        pass
    
    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, 
                    clientId, whyHeld, mktCapPrice):
        om = getattr(self, 'ordManager', None)
        if om is not None:
            om.OrderStatus(orderId, status, filled, remaining, avgFillPrice)
            
    def execDetails(self, reqid, contract, execution):
        om = getattr(self, "ordManager", None)
        if om is not None:
            om.ExecDetails(execution.orderId, execution.shares, execution.price)
            
    def updateAccountValue(self, key, val, currency, accountName):
        super().updateAccountValue(key, val, currency, accountName)
        
        mapping = {'account': accountName, 
                   'tag' : key, 
                   'value' : val, 
                   'currency' : currency}
        
        if ((self.dfAccountValues['account'] == accountName) & 
            (self.dfAccountValues['tag'] == key) &
            (self.dfAccountValues['currency'] == currency)).any():
            self.dfAccountValues.loc[(self.dfAccountValues['account'] == accountName) & 
                                     (self.dfAccountValues['tag'] == key) &
                                     (self.dfAccountValues['currency'] == currency), 'value'] = val
        else:
            self.dfAccountValues = pd.concat((self.dfAccountValues, pd.Dataframe([mapping])), ignore_index = True)
            
    def accountDownloadEnd(self, accountName):
        super().accountDOwnloadEnd(accountName)
        self.accountUpdateEndEvent.set()
        
    def reqAccountUpdatesSync(self, account, timeout = 2.0):
        self.accountUpdateEndEvent.clear()
        self.reqAccountUpdates(True, account)
        self.accountUpdateEndEvent.wait(timeout)
        self.reqAccountUpdates(False, account)