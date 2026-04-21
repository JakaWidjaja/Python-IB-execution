import time
import pandas as pd
from threading import Event

class MarketData:
    reqIdCounter = 100
    
    def __init__(self):
        pass
    
    def TickStream(self, tws, contractDict):
        tws          = tws
        contractDict = contractDict
        
        for symbol, contract in contractDict.items():
            
            tws.reqIdToSymbol[MarketData.reqIdCounter] = symbol
            
            tws.reqTickByTickData(reqId         = MarketData.reqIdCounter, 
                                       contract      = contract, 
                                       tickType      = "AllLast", 
                                       numberOfTicks = 0,
                                       ignoreSize    = True)
            
            MarketData.reqIdCounter += 1  # Increment the global counter
    
    def GetFuturesLast(self, tws, symbol, contract, marketDataType, timeout = 5.0, genericTickList = '', 
                       regulatorySnapshot = False, mktDataOptions = []):
        
        tws.reqMarketDataType(marketDataType)
        
        reqId = MarketData.reqIdCounter
        MarketData.reqIdCounter += 1
        
        tws.reqIdToSymbol[reqId] = symbol
        tws.eventLast[symbol]    = Event()
        
        tws.reqMktData(reqId              = reqId, 
                       contract           = contract, 
                       genericTickList    = genericTickList, 
                       snapshot           = False,
                       regulatorySnapshot = regulatorySnapshot, 
                       mktDataOptions     = mktDataOptions)
        
        ok = tws.eventLast[symbol].wait(timeout = timeout)

        if not ok:
            raise TimeoutError(f'Timeout waiting LAST for {symbol}')
            
        return float(tws.mktDataLast.get(symbol, 0.0))
    
    def GetFuturesBid(self, tws, symbol, contract, marketDataType, timeout = 5.0, genericTickList = '', 
                       regulatorySnapshot = False, mktDataOptions = []):
        
        tws.reqMarketDataType(marketDataType)
        
        reqId = MarketData.reqIdCounter
        MarketData.reqIdCounter += 1
        
        tws.reqIdToSymbol[reqId] = symbol
        tws.eventBidAsk[symbol]  = Event()
        
        tws.reqMktData(reqId              = reqId, 
                       contract           = contract, 
                       genericTickList    = genericTickList, 
                       snapshot           = False, 
                       regulatorySnapshot = regulatorySnapshot,
                       mktDataOptions     = mktDataOptions)
        
        ok = tws.eventBidAsk[symbol].wait(timeout = timeout)
        
        if not ok:
            raise TimeoutError(f'Timeout waiting BID for {symbol}')
            
        bid = float(tws.mktDataBid.get(symbol, -1.0))
        if bid <= 0:
            raise ValueError(f'Invalid BID for {symbol} : {bid}')
            
        return bid
    
    def GetFuturesAsk(self, tws, symbol, contract, marketDataType, timeout = 5.0, genericTickList = '', 
                       regulatorySnapshot = False, mktDataOptions = []):
        
        tws.reqMarketDataType(marketDataType)

        reqId = MarketData.reqIdCounter
        MarketData.reqIdCounter += 1
    
        tws.reqIdToSymbol[reqId] = symbol
        tws.eventBidAsk[symbol]  = Event()
    
        tws.reqMktData(reqId              = reqId,
                       contract           = contract,
                       genericTickList    = genericTickList,
                       snapshot           = False,
                       regulatorySnapshot = regulatorySnapshot,
                       mktDataOptions     = mktDataOptions)
    
        ok = tws.eventBidAsk[symbol].wait(timeout = timeout)
    
        if not ok:
            raise TimeoutError(f'Timeout waiting ASK for {symbol}')
    
        ask = float(tws.mktDataAsk.get(symbol, -1.0))
        if ask <= 0:
            raise ValueError(f'Invalid ASK for {symbol}: {ask}')
    
        return ask
    
    def GetOptionBidAsk(self, tws, contractDict, marketDataType, timeout=5.0,
                    genericTickList='', regulatorySnapshot=False, mktDataOptions=None,
                    cancelAfter=True):

        if mktDataOptions is None:
            mktDataOptions = []
    
        tws.reqMarketDataType(marketDataType)
    
        symbols = list(contractDict.keys())
        for s in symbols:
            tws.eventBidAsk[s] = Event()
    
        # keep reqIds so we can cancel precisely
        reqIds = {}
    
        for symbol, contract in contractDict.items():
            reqId = MarketData.reqIdCounter
            MarketData.reqIdCounter += 1
    
            tws.reqIdToSymbol[reqId] = symbol
            reqIds[symbol] = reqId
    
            tws.reqMktData(reqId=reqId,
                           contract=contract,
                           genericTickList=genericTickList,
                           snapshot=False,
                           regulatorySnapshot=regulatorySnapshot,
                           mktDataOptions=mktDataOptions)
    
        deadline = time.time() + timeout
        pending = set(symbols)
    
        while pending and time.time() < deadline:
            done = [s for s in pending if tws.eventBidAsk[s].is_set()]
            for s in done:
                pending.remove(s)
            if pending:
                time.sleep(0.01)
    
        # cancel streams regardless (especially on timeout)
        if cancelAfter:
            for s, rid in reqIds.items():
                try:
                    tws.cancelMktData(rid)
                except Exception:
                    pass
    
        if pending:
            raise TimeoutError(f"Timeout waiting Bid/Ask for: {sorted(pending)}")
    
        return True   
    
    def GetExpirationDate(self, tws, contract, timeout=5.0):
        reqId = tws.getNextReqId()
    
        # init storage + event for this reqId
        with tws.contractDetailsLock:
            tws.contractDetailsData[reqId] = []
        tws.contractDetailsEndEvent[reqId] = Event()
    
        tws.reqContractDetails(reqId, contract)
    
        ok = tws.contractDetailsEndEvent[reqId].wait(timeout=timeout)
        if not ok:
            raise TimeoutError("Timeout waiting contractDetailsEnd")
    
        with tws.contractDetailsLock:
            matches = tws.contractDetailsData.get(reqId, [])
    
        if len(matches) == 0:
            raise ValueError("No contractDetails returned (0 matches)")
    
        cd = matches[0]
        # best field for SR3
        if getattr(cd, "realExpirationDate", None):
            return cd.realExpirationDate
    
        # fallback (rare)
        return cd.contract.lastTradeDateOrContractMonth
    
    def GetStockPrice(self, tws, symbol, contract, marketDataType, timeout=8.0, genericTickList = '',
                      regulatorySnapshot = False, mktDataOptions = None, snapshot = False):

        if mktDataOptions is None:
            mktDataOptions = []
    
        tws.reqMarketDataType(marketDataType)
    
        reqId = MarketData.reqIdCounter
        MarketData.reqIdCounter += 1
    
        tws.reqIdToSymbol[reqId] = symbol
        tws.eventLast[symbol] = Event()
        tws.eventBidAsk[symbol] = Event()
    
        tws.reqMktData(reqId              = reqId,
                       contract           = contract,
                       genericTickList    = genericTickList,
                       snapshot           = snapshot,
                       regulatorySnapshot = regulatorySnapshot,
                       mktDataOptions     = mktDataOptions)
    
        deadline = time.time() + timeout
    
        while time.time() < deadline:
            last = float(tws.mktDataLast.get(symbol, 0.0))
            bid  = float(tws.mktDataBid.get(symbol, 0.0))
            ask  = float(tws.mktDataAsk.get(symbol, 0.0))
    
            if last > 0:
                return last
    
            if bid > 0 and ask > 0:
                return 0.5 * (bid + ask)
    
            time.sleep(0.05)
    
        raise TimeoutError(f"Timeout waiting usable stock price for {symbol}")

    def GetMarketData(self, tws, contractDict, marketDataType, timeDelay, 
                      genericTickList = '', snapshot = False, regulatorySnapshot = False, mktDataOptions = []):
        tws                = tws
        contractDict       = contractDict
        marketDataType     = marketDataType
        timeDelay          = timeDelay
        genericTickList    = genericTickList
        snapshot           = snapshot
        regulatorySnapshot = regulatorySnapshot
        mktDataOptions     = mktDataOptions
        
        tws.reqMarketDataType(marketDataType)

        for symbol, contract in contractDict.items():
            # Store the mapping of reqId to the stock symbol in the twsWrapper object
            tws.reqIdToSymbol[MarketData.reqIdCounter] = symbol
            
            tws.reqMktData(reqId              = MarketData.reqIdCounter, 
                           contract           = contract, 
                           genericTickList    = genericTickList, 
                           snapshot           = snapshot, 
                           regulatorySnapshot = regulatorySnapshot, 
                           mktDataOptions     = mktDataOptions)

            MarketData.reqIdCounter += 1  # Increment the global counter
            
        time.sleep(timeDelay)
    
    def GetOptMktData(self, tws, contractDict, marketDataType, timeDelay, 
                      genericTickList = '', snapshot = False, regulatorySnapshot = False, mktDataOptions = []):
        tws                = tws
        contractDict       = contractDict
        marketDataType     = marketDataType
        timeDelay          = timeDelay
        genericTickList    = genericTickList
        snapshot           = snapshot
        regulatorySnapshot = regulatorySnapshot
        mktDataOptions     = mktDataOptions
        
        tws.reqMarketDataType(marketDataType)
        
        for symbol, contract in contractDict.items():
            # Store the mapping of reqId to the stock symbol in the twsWrapper object
            tws.reqIdToSymbol[MarketData.reqIdCounter] = symbol
            
            tws.reqMktData(reqId              = MarketData.reqIdCounter, 
                           contract           = contract, 
                           genericTickList    = genericTickList, 
                           snapshot           = snapshot, 
                           regulatorySnapshot = regulatorySnapshot, 
                           mktDataOptions     = mktDataOptions)

            MarketData.reqIdCounter += 1  # Increment the global counter
            
        time.sleep(timeDelay)

    def SortMarketData(self, bid, ask, last, contractDictionary):
        bid                = bid
        ask                = ask
        last               = last
        contractDictionary = contractDictionary
        
        columnNames = ['ticker', 'bid', 'ask', 'mid', 'last']
        output = pd.DataFrame(columns=columnNames)
    
        for ticker in contractDictionary.keys():
            bidPrice  = bid.get(ticker, 0)
            askPrice  = ask.get(ticker, 0)
            lastPrice = last.get(ticker, 0)
    
            # Calculate the mid price correctly
            midPrice = (askPrice + bidPrice) / 2 if askPrice > 0 and bidPrice > 0 else 0
    
            temp = pd.DataFrame([[ticker, bidPrice, askPrice, midPrice, lastPrice]], columns=columnNames)
            output = pd.concat([output, temp], ignore_index=True)
            
        return output
    
    def SortMktOptionData(self, contractDict, bid, ask, last, underlying, optionPrice, 
                          impVol, delta, gamma, vega, theta, div):
        contractDict = contractDict
        bid          = bid
        ask          = ask
        last         = last
        underlying   = underlying
        optionPrice  = optionPrice
        impVol       = impVol
        delta        = delta
        gamma        = gamma
        vega         = vega
        theta        = theta
        div          = div
        
        columnNames = ['ticker', 'bid', 'ask', 'mid', 'last', 'underlying', 'option price', 'imp vol',
                       'delta', 'gamma', 'vega', 'theta', 'dividend']
        output = pd.DataFrame(columns = columnNames)
        
        for ticker in contractDict.keys():
            tickName  = ticker
            bidPrice  = bid.get(ticker, 0)
            askPrice  = ask.get(ticker, 0)
            lastPrice = last.get(ticker, 0)
            impVol    = impVol[ticker]
            delta     = delta[ticker]
            gamma     = gamma[ticker]
            vega      = vega[ticker]
            theta     = theta[ticker]
            undPrice  = underlying[ticker]
            optPrice  = optionPrice[ticker]
            divPrice  = div[ticker]
            
            # Calculate the mid price correctly
            midPrice = (askPrice + bidPrice) / 2 if askPrice > 0 and bidPrice > 0 else 0
            
            temp = pd.DataFrame([[tickName, bidPrice, askPrice, midPrice, lastPrice, undPrice, optPrice,
                                  impVol, delta, gamma, vega, theta, divPrice]], columns = columnNames)
            
            output = pd.concat([output, temp], ignore_index = True)
            
        return output