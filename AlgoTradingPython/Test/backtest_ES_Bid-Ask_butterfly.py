#Set directory
import os
os.chdir('/home/lun/Desktop/Folder 2/AlgoTradingPython')
directory = os.getcwd() 

# Models
from Strategy.OptionRiskNeutral.GeneralisedGamma import GeneralisedGamma
from Strategy.OptionRiskNeutral.OptionArbitrage  import OptionArbitrage
from Strategy.OptionRiskNeutral.TradeManagement  import TradeManagement
from Strategy.OptionRiskNeutral.TradeTracker     import TradeTracker

import numpy  as np
import pandas as pd
import datetime as dt
import re
#======================================================================================
#**************************************************************************************
# Get Data
tradeDate = '20260228'

data = pd.read_csv(directory + '/TradeTracking/OptionRiskNeutral/OptionLedger_surface_' + tradeDate + '.csv')
data['ts'] = pd.to_datetime(data['ts'])
data['time'] = data['ts'].dt.time
data['date'] = data['ts'].dt.date

data = data.rename(columns = {'futures price' : 'futures'})

# Extract options columns (mkt only)
pattern = r'(call|put)_(\d+)_mkt_(bid|ask)'
optCols = [c for c in data.columns if re.match(pattern, c)]
dfLong = data.melt(id_vars    = ['date', 'time', 'futures'], 
                   value_vars = optCols, 
                   var_name   = 'raw', 
                   value_name = 'price')

# Extract components
dfLong[['opt_type', 'strike', 'side']] = dfLong['raw'].str.extract(pattern)
dfLong['strike'] = dfLong['strike'].astype(int)

# Pivot bid/ask into columns
data = dfLong.pivot_table(index   = ['date', 'time', 'futures', 'opt_type', 'strike'], 
                          columns = 'side', 
                          values  = 'price').reset_index()

# Clean column names
data.columns.name = None

# Interest Rate (proxy)
intRate = 0.0367
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
# Trading Parameters
gg = GeneralisedGamma()

# GG model parameters
straddleTriggerLevel        = 0.0
convexTriggerLevel          = 0.0
skewTriggerLevelUpper       = 0.0#1.0
skewTriggerLevelLower       = 0.0#-1.0

rrThresholdUpper            = 0.0
rrThresholdLower            = 0.0
butterflyPutThresholdUpper  = 0.0#0.10
butterflyPutThresholdLower  = 0.0#-0.08
butterflyCallThresholdUpper = 0.0#0.20
butterflyCallThresholdLower = 0.0#0.00


# exit threshold
exitButterflyPutBuy   = 0.00
exitButterflyPutSell  = 0.0#-0.07
exitButterflyCallBuy  = 0.0#0.02
exitButterflyCallSell = 0.0#0.05

# Stop loss and profit taking
stopLossPerc     = 0.0#0.30
profitTakingPerc = 0.0#0.20

# Session settings
calibrateTime  = dt.time(2, 0, 0)
noNewEntryTime = dt.time(7, 45, 0)
forceLiqTime   = dt.time(8, 0, 0)

# Others
numStrikes   = 10
multiplier   = 50
commission   = 6.0
contractQty  = 1        # Assume trading 1 butterfly contract only (need to incorporate market depth)
optionExpiry = dt.date(2026, 3, 20) 
yearCount    = 360
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
# Backtesting adapters & helpers

class ImmediateEvent:
    def __init__(self):
        self.flag = False
    
    def clear(self):
        self.flag = False
    
    def wait(self, timeout = None):
        return self.flag
    
    def set(self):
        self.flag = True
        
class OptionContract:
    def __init__(self, symbol, currency, localSymbol):
        self.symbol      = symbol
        self.currency    = currency
        self.localSymbol = localSymbol
        
class BagContract:
    def __init__(self, contractDict, symbol, currency):
        self.contractDict = contractDict
        self.symbol       = symbol
        self.currency     = currency
        
class BacktestTWS:
    '''
    Using the existing classes that use TWS, but adapted to run against historical bid/ask data
    '''
    def __init__(self):
        self.mktDataBid         = {}
        self.mktDataAsk         = {}
        self.mktDataLast        = {}
        self.nextValidOrderId = 1
        self.orderIdEvent       = ImmediateEvent()
        self.ordManager         = None
        
        self.currentTS = None
        self.submitted  = {}
        
    def reqIds(self, _):
        self.orderIdEvent.set()
        
    def cancelOrder(self, orderId):
        if self.ordManager is not None:
            self.ordManager.OrderStatus(orderId, 'Cancelled', 0.0, 0.0, 0.0)
            
    def placeOrder(self, orderId, contract, orderObject):
        self.submitted[orderId] = {'contract' : contract, 
                                   'order'    : orderObject, 
                                   'ts'       : self.currentTS}
        
    def set_market(self, ts, futuresPrice, optionSlice):
        self.currentTS = pd.Timestamp(ts)
        
        self.mktDataLast['ES']      = float(futuresPrice)
        self.mktDataLast['futures'] = float(futuresPrice)
        
        self.mktDataBid  = {}
        self.mktDataAsk  = {}
        self.mktDataLast = {'ES' : float(futuresPrice), 'futures' : float(futuresPrice)}
        
        for _, row in optionSlice.iterrows():
            sym = f"{row['opt_type']}_{int(row['strike'])}"
            bid = float(row['bid'])
            ask = float(row['ask'])
            
            self.mktDataBid[sym]  = bid
            self.mktDataAsk[sym]  = ask
            self.mktDataLast[sym] = 0.5 * (bid + ask)
            
    def QuoteBag(self, bagContract):
        spreadBid = 0.0
        spreadAsk = 0.0
        
        for legKey, legContract in bagContract.contractDict.items():
            sym = getattr(legContract, 'localSymbol', None)
            if sym is None:
                raise ValueError(f'missing localSymbol for leg {legKey}')
            
            bid = float(self.mktDataBid.get(sym, 0.0))
            ask = float(self.mktDataAsk.get(sym, 0.0))
            if bid <= 0.0 and ask <= 0.0:
                return None
            
            sign = +1 if str(legKey).startswith('long') else -1
            if sign > 0:
                spreadBid += bid
                spreadAsk += ask
            else:
                spreadBid -= ask
                spreadAsk -= bid
                
        spreadMid = 0.5 * (spreadBid + spreadAsk)
        return spreadBid, spreadAsk, spreadMid
    
    def SettleSubmittedOrder(self):
        '''
        After TradeManagement submits + registers orders, call this once to convert
        those submitted orders into Filled / Submitted statuses based on the current row.
        '''
        
        if self.ordManager is None:
            return
        
        for orderId, spec in list(self.submitted.items()):
            managed = self.ordManager.orders.get(orderId)
            if managed is None:
                continue
            
            # Do not re-settle orders already finalised
            if managed.status in {'Filled', 'Cancelled', 'ApiCancelled', 'Inactive'}:
                continue
            
            bag         = spec['contract']
            orderObject = spec['order']
            quote = self.QuoteBag(bag)
            if quote is None:
                self.ordManager.OrderStatus(orderId, 'Inactive', 0.0, orderObject.totalQuantity, 0.0)
                continue
            
            spreadBid, spreadAsk, _ = quote
            action    = str(orderObject.action).upper()
            orderType = str(orderObject.orderType).upper()
            qty       = float(orderObject.totalQuantity)
            
            fillPrice  = None
            shouldFill = False
            
            if orderType == 'MKT':
                if action == 'BUY':
                    fillPrice = spreadAsk
                elif action == 'SELL':
                    fillPrice = spreadBid
                shouldFill = True
            
            elif orderType == 'LMT':
                lmt = float(getattr(orderObject, 'lmtPrice', 0.0))
                if action == 'BUY' and lmt >= spreadAsk:
                    fillPrice = spreadAsk
                    shouldFill = True
                elif action == 'SELL' and lmt <= spreadBid:
                    fillPrice = spreadBid
                    shouldFill = True
            
            if shouldFill and fillPrice is not None:
                self.ordManager.OrderStatus(orderId, 'Filled', qty, 0.0, float(fillPrice))
                self.ordManager.ExecDetails(orderId, qty, float(fillPrice))
            else:
                self.ordManager.OrderStatus(orderId, 'Submitted', 0.0, qty, 0.0)
                
class BacktestTradeTracker(TradeTracker):
    '''
    Same idea as TradeTracker, but uses historical timestamp from backtest row 
    '''
    def __init__(self, outLocation, prefix = 'ledger'):
        super().__init__(outLocation, prefix)
        self.currentTS = None
        
    def SetCurrentTS(self, ts):
        self.currentTS = pd.Timestamp(ts)
        
    def MakeTradeId(self, signalKey, entryOrderId):
        ts = (self.currentTS or pd.Timestamp.utcnow()).strftime('%Y%m%d_%H%M%S_%f')
        return f'{signalKey}_{ts}_{entryOrderId}' 
        
    def Append(self, row):
        if 'ts' not in row:
            row['ts'] = self.currentTS
        self.rows.append(row)
        
    def SurfaceNewRow(self, futuresPrice):
        if self.surfCols is None:
            raise RuntimeError('InitMarketSurface() must be called first')
            
        row = [None] * len(self.surfCols)
        row[0] = self.currentTS
        row[1] = futuresPrice
        return row

def AnyGlobalPositionOpen(inTrade, activeEntryOrder, exitInProgress):
    return (any(bool(v) for v in inTrade.values()) or 
            any(len(v) > 0 for v in activeEntryOrder.values()) or
            any(bool(v) for v in exitInProgress.values()))

def ExecutableExitMark(direction, spreadBid, spreadAsk):
    '''
    Return the executable close price for an open spread
    Buy entry  -> close by SELLING at spreadBid
    Sell entry -> close by BUYING at spreadAsk
    '''
    direction = str(direction).upper()
    
    if direction == 'BUY':
        return None if spreadBid is None else float(spreadBid)
    if direction == 'SELL':
        return None if spreadAsk is None else float(spreadAsk)
    return None

def SignedMarkValue(direction, spreadBid, spreadAsk, qty, multiplier):
    exitMark = ExecutableExitMark(direction, spreadBid, spreadAsk)
    if exitMark is None:
        return 0.0
    
    direction = str(direction).upper()
    
    if direction  == 'BUY':
        return -exitMark * qty * multiplier
    elif direction == 'SELL':
        return exitMark * qty * multiplier
    
    return 0.0

def TradePNL(direction, entryFill, spreadBid, spreadAsk, qty, multiplier, commission = 6.0):
    exitMark = ExecutableExitMark(direction, spreadBid, spreadAsk)
    if entryFill is None or exitMark is None:
        return 0.0
    
    direction = str(direction).upper()
    
    if direction == 'BUY':
        gross = (exitMark - float(entryFill)) * qty * multiplier
    elif direction == 'SELL':
        gross = (float(entryFill) - exitMark) * qty * multiplier
    else:
        gross = 0.0
    
    return gross - float(commission) * qty

def StateRowContinuous(signalKey, ts, tradeMgt, optionPrices, valuationMap,
                       inTrade, tradeSignalDict, entryFillPrice, stopLossPrice,
                       totalRealisedPnl, multiplier, commission=6.0,
                       profitTakingPerc=0.20):
    """
    Continuous per-bar log:
    - if in trade, value the live trade in tradeSignalDict
    - otherwise value the current signal in signalMap (if any)
    - always populate market/model bid/ask/mid and diff when a structure exists
    """

    liveSig = tradeSignalDict.get(signalKey)
    curSig  = valuationMap.get(signalKey)

    active = bool(inTrade.get(signalKey, False)) and isinstance(liveSig, dict) and bool(liveSig)

    if active:
        sig = liveSig
    elif isinstance(curSig, dict) and curSig:
        sig = curSig
    else:
        sig = None

    direction = str(sig.get('direction', 'NA')).upper() if isinstance(sig, dict) else 'NA'
    qty       = int(liveSig.get('numContract', 1)) if active and isinstance(liveSig, dict) else 0

    mktBid = mktAsk = mktMid = None
    mdlBid = mdlAsk = mdlMid = None
    diff = None

    pnl = 0.0
    portfolioValue = 0.0
    entryValue = 0.0
    entryDiff = 0.0

    if isinstance(sig, dict):
        mktQuote = tradeMgt.ButterflyQuote(sig)
        if mktQuote is not None:
            mktBid, mktAsk, mktMid = mktQuote

        mdlQuote = tradeMgt.ButterflyModelQuote(sig, optionPrices)
        if mdlQuote is not None:
            mdlBid, mdlAsk, mdlMid = mdlQuote

        # executable-side diff to match your updated logic
        if mktBid is not None and mdlBid is not None and direction == 'BUY':
            diff = float(mktBid) - float(mdlBid)
        elif mktAsk is not None and mdlAsk is not None and direction == 'SELL':
            diff = float(mktAsk) - float(mdlAsk)

    if active:
        fill = entryFillPrice.get(signalKey)
        pnl = TradePNL(direction, fill, mktBid, mktAsk, qty, multiplier, commission=commission)
        portfolioValue = SignedMarkValue(direction, mktBid, mktAsk, qty, multiplier)

        if fill is not None:
            if direction == 'BUY':
                entryValue = -float(fill) * qty * multiplier
            elif direction == 'SELL':
                entryValue = float(fill) * qty * multiplier

        # entry diff should also use executable side
        if fill is not None:
            if direction == 'BUY' and mdlBid is not None:
                entryDiff = float(fill) - float(mdlBid)
            elif direction == 'SELL' and mdlAsk is not None:
                entryDiff = float(fill) - float(mdlAsk)

    row = {
        'ts': pd.Timestamp(ts),
        'signalKey': signalKey,
        'direction': direction,
        'butterfly entry': active,
        'portfolio value': portfolioValue,
        'pnl': pnl,
        'total pnl': float(totalRealisedPnl),
        'commission': (float(commission) * qty) if active else 0.0,
        'stop method': None,
        'stop loss': stopLossPrice.get(signalKey),
        'contract #': qty,
        'market butterfly bid': mktBid,
        'market butterfly ask': mktAsk,
        'market butterfly': mktMid,
        'market butterfly exit': ExecutableExitMark(direction, mktBid, mktAsk) if isinstance(sig, dict) else None,
        'model butterfly bid': mdlBid,
        'model butterfly ask': mdlAsk,
        'model butterfly': mdlMid,
        'diff': diff,
        'entry fill': entryFillPrice.get(signalKey),
        'entry value': entryValue,
        'entry diff': entryDiff,
        'profit target': None if entryFillPrice.get(signalKey) is None else
                         float(entryFillPrice.get(signalKey)) * profitTakingPerc * qty * multiplier,
        'long call 1': sig.get('long call 1') if isinstance(sig, dict) else None,
        'short call 1': sig.get('short call 1') if isinstance(sig, dict) else None,
        'long call 2': sig.get('long call 2') if isinstance(sig, dict) else None,
        'short call 2': sig.get('short call 2') if isinstance(sig, dict) else None,
        'long put 1': sig.get('long put 1') if isinstance(sig, dict) else None,
        'short put 1': sig.get('short put 1') if isinstance(sig, dict) else None,
        'long put 2': sig.get('long put 2') if isinstance(sig, dict) else None,
        'short put 2': sig.get('short put 2') if isinstance(sig, dict) else None,
    }
    return row

def BuildContinuousButterflyMap(optionPrices, futuresPrice):
    calls = sorted([float(k) for t, k in optionPrices.index if t == 'call'])
    puts  = sorted([float(k) for t, k in optionPrices.index if t == 'put'])

    if not calls or not puts:
        return {'callBuy': None, 'callSell': None, 'putBuy': None, 'putSell': None}

    strikes = sorted(set(calls))  # call/put strikes should match in your data
    atmStrike = min(strikes, key=lambda k: abs(k - futuresPrice))
    atmIndex = strikes.index(atmStrike)

    out = {'callBuy': None, 'callSell': None, 'putBuy': None, 'putSell': None}

    # Put side: atm-3, atm-2, atm-1
    if atmIndex >= 3:
        p1, p2, p3 = strikes[atmIndex - 3], strikes[atmIndex - 2], strikes[atmIndex - 1]

        out['putBuy'] = {
            'long put 1': p1,
            'long put 2': p3,
            'short put 1': p2,
            'short put 2': p2,
            'direction': 'BUY'
        }

        out['putSell'] = {
            'short put 1': p1,
            'short put 2': p3,
            'long put 1': p2,
            'long put 2': p2,
            'direction': 'SELL'
        }

    # Call side: atm+1, atm+2, atm+3
    if atmIndex <= len(strikes) - 4:
        c1, c2, c3 = strikes[atmIndex + 1], strikes[atmIndex + 2], strikes[atmIndex + 3]

        out['callBuy'] = {
            'long call 1': c1,
            'long call 2': c3,
            'short call 1': c2,
            'short call 2': c2,
            'direction': 'BUY'
        }

        out['callSell'] = {
            'short call 1': c1,
            'short call 2': c3,
            'long call 1': c2,
            'long call 2': c2,
            'direction': 'SELL'
        }

    return out


#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
# Backtesting 

tradeDates = sorted(data['date'].unique())

# Option contracts from data
optionContracts = {}
for optType, strike in sorted(data[['opt_type', 'strike']].drop_duplicates().itertuples(index = False), 
                              key = lambda x : (x[0], x[1])):
    localSymbol = f'{optType}_{int(strike)}'
    optionContracts[localSymbol] = OptionContract(symbol = 'ES', currency = 'USD', localSymbol = localSymbol)

# Backtest TWS + tracker    
tws = BacktestTWS()
tracker = BacktestTradeTracker(outLocation = '/home/lun/Desktop/Folder 2/AlgoTradingPython/Test/Backtest Results', 
                               prefix      = 'Option_Backtest_Ledger')

tracker.InitMarketSurface(optionContracts)
tradeMgt = TradeManagement(tws, optionContracts, tracker)

# Patch Orders.MakeButterflyContract so existing Orders.py can be used without IBKR Contracts. 
tradeMgt.order.mkContract.MakeButterflyContract = lambda contractDict, symbol, \
                                                currency: BagContract(contractDict, symbol, currency)
                                                
signals          = ['callBuy', 'callSell', 'putBuy', 'putSell']
inTrade          = {s: False for s in signals}
activeEntryOrder = {s: [] for s in signals}
entryWinner      = {s: None for s in signals}
batchStart       = {s: None for s in signals}
lastSignals      = {s: None for s in signals}

entryFillPrice  = {s: None for s in signals}
stopLossPrice   = {s: None for s in signals}
stopArmed       = {s: False for s in signals}
tradeSignalDict = {s: None for s in signals}
exitOrderId     = {s: None for s in signals}
exitInProgress  = {s: False for s in signals}

stateRows   = []
summaryRows = []

for d in tradeDates:
    dayData = data.loc[data['date'] == d].copy()
    tradingTimes = sorted(dayData['time'].unique())
    
    if len(tradingTimes) == 0:
        continue
    
    dayStartRealised = float(tracker.realisedCumPnl)
    
    expiry = (optionExpiry - pd.Timestamp(d).date()).days / yearCount
    
    # Calibrate once for the day
    calibTime = None
    xiBid = alphaBid = resBid = None
    xiAsk = alphaAsk = resAsk = None
    
    for ts in tradingTimes:
        t = ts
        if t < calibrateTime:
            continue
        
        snap = dayData.loc[dayData['time'] == ts].copy()
        futuresPrice = float(snap['futures'].iloc[0])
        
        putSnap  = snap.loc[(snap['opt_type'] == 'put')  & (snap['strike'] < futuresPrice)].sort_values('strike')
        callSnap = snap.loc[(snap['opt_type'] == 'call') & (snap['strike'] > futuresPrice)].sort_values('strike')
        
        calibSnap = pd.concat([putSnap, callSnap], ignore_index = True)
        if calibSnap.empty:
            continue
        
        strikeList     = calibSnap['strike'].astype(float).tolist()
        bidPrice       = calibSnap['bid'].astype(float).tolist()
        askPrice       = calibSnap['ask'].astype(float).tolist()
        optionTypeList = calibSnap['opt_type'].astype(str).tolist()
        
        try:
            xiBid, alphaBid, resBid = gg.Calibrate(bidPrice, futuresPrice, strikeList, expiry, intRate, optionTypeList)
            xiAsk, alphaAsk, resAsk = gg.Calibrate(askPrice, futuresPrice, strikeList, expiry, intRate, optionTypeList)
            calibTime = ts
            break
        except:
            continue
        
    if calibTime is None:
        continue
    
    # Trading 
    optArb = OptionArbitrage(straddleTriggerLevel,
                             convexTriggerLevel,
                             skewTriggerLevelUpper,
                             skewTriggerLevelLower,
                             rrThresholdUpper,
                             rrThresholdLower,
                             butterflyPutThresholdUpper,
                             butterflyPutThresholdLower,
                             butterflyCallThresholdUpper,
                             butterflyCallThresholdLower,
                             expiry,
                             intRate)
    
    for ts in tradingTimes:
        currentTime = ts
        currentTS = pd.Timestamp.combine(pd.Timestamp(d).date(), currentTime)
        snap = dayData.loc[dayData['time'] == currentTime].copy()
        if snap.empty:
            continue
        
        futuresPrice = float(snap['futures'].iloc[0])
        
        # Feed the adapter the current row market
        tws.set_market(currentTS, futuresPrice, snap)
        tracker.SetCurrentTS(currentTS)
        
        # Build optionPrices table for this timestamp
        optionPrices = snap[['opt_type', 'strike', 'bid', 'ask']].copy()
        optionPrices['type']    = optionPrices['opt_type'].astype(str)
        optionPrices['strike']  = optionPrices['strike'].astype(int).astype(str)
        optionPrices['mkt bid'] = optionPrices['bid'].astype(float)
        optionPrices['mkt ask'] = optionPrices['ask'].astype(float)
        optionPrices['mkt mid'] = 0.5 * (optionPrices['mkt bid'] + optionPrices['mkt ask'])
        
        optionPrices['model bid'] = optionPrices.apply(lambda r: gg.OptionPrice(futuresPrice, 
                                                                                float(r['strike']),
                                                                                expiry, 
                                                                                intRate, 
                                                                                xiBid, 
                                                                                alphaBid, 
                                                                                r['type']), axis = 1)
        
        optionPrices['model ask'] = optionPrices.apply(lambda r: gg.OptionPrice(futuresPrice, 
                                                                                float(r['strike']),
                                                                                expiry, 
                                                                                intRate, 
                                                                                xiAsk, 
                                                                                alphaAsk, 
                                                                                r['type']), axis = 1)
        
        optionPrices = optionPrices.set_index(['type', 'strike'])[['mkt bid', 'mkt ask', 'mkt mid', 'model bid', 'model ask']]
        
        # Surface logging
        surfRow = tracker.SurfaceNewRow(futuresPrice)
        for sym in sorted(optionContracts.keys()):
            optType, strike = sym.split('_')
            row = optionPrices.loc[(optType, strike)]
            tracker.SurfaceSet(surfRow, 
                               sym,
                               float(row['mkt bid']), 
                               float(row['mkt ask']), 
                               float(row['model bid']), 
                               float(row['model ask']))
        
        tracker.SurfaceAppendRow(surfRow)
        
        # Signal generation
        optArb.ParamSetUp(optionPrices, futuresPrice, expiry, intRate)
        res = optArb.Arbitrage()
        butterflyCallBuy, butterflyCallSell, butterflyPutBuy, butterflyPutSell = res['skew']['butterfly']

        signalMap = {'callBuy': butterflyCallBuy,
                     'callSell': butterflyCallSell,
                     'putBuy': butterflyPutBuy,
                     'putSell': butterflyPutSell}
        
        valuationMap = BuildContinuousButterflyMap(optionPrices, futuresPrice)
        
        # Per-bar market/event tracker logging for current/active trade
        for sk, sig in signalMap.items():
            sigTrade = tradeSignalDict.get(sk)
            sigUse = sigTrade if isinstance(sigTrade, dict) and sigTrade else sig
            if not isinstance(sigUse, dict) or not sigUse:
                continue
            
            mktQ = tradeMgt.ButterflyQuote(sigUse)
            modQ = tradeMgt.ButterflyModelQuote(sigUse, optionPrices)
            if mktQ is None or modQ is None:
                continue
            
            mktBid, mktAsk, mktMid = mktQ
            modBid, modAsk, modMid = modQ
            diff = float(mktMid) - float(modMid)
            
            tracker.OnMarket(signalKey    = sk,
                             futuresPrice = futuresPrice,
                             mktBid       = mktBid,
                             mktAsk       = mktAsk,
                             mktMid       = mktMid,
                             modelBid     = modBid,
                             modelAsk     = modAsk,
                             modelMid     = modMid,
                             diff         = diff    )
        
        # Entry
        allowNewEntry = currentTime < noNewEntryTime
        if allowNewEntry:
            for sk in signals:
                # Manage already-tracked state for this bucket first
                tradeMgt.ManageEntry(sk, 
                                     signalMap.get(sk, {}),
                                     inTrade, 
                                     activeEntryOrder, 
                                     entryWinner, 
                                     batchStart, 
                                     lastSignals, 
                                     entryFillPrice, 
                                     stopLossPrice, 
                                     stopArmed, 
                                     tradeSignalDict, 
                                     exitInProgress, 
                                     numContract  = contractQty, 
                                     ttlSeconds   = 0.0, 
                                     stopLossPerc = stopLossPerc)
                
                # Settle newly submitted orders from this pass
                tws.SettleSubmittedOrder()
                
                # Promote any immediate fills on the same timestamp
                tradeMgt.ManageEntry(sk,
                                     signalMap.get(sk, {}),
                                     inTrade,
                                     activeEntryOrder,
                                     entryWinner,
                                     batchStart,
                                     lastSignals,
                                     entryFillPrice,
                                     stopLossPrice,
                                     stopArmed,
                                     tradeSignalDict,
                                     exitInProgress,
                                     numContract  = contractQty,
                                     ttlSeconds   = 0.0,
                                     stopLossPerc = stopLossPerc )
                
                # Once anythin is live / exiting / tracked, block all other fresh entries. 
                if AnyGlobalPositionOpen(inTrade, activeEntryOrder, exitInProgress):
                    break
                
        # Cancel outstanding entry orders after entry cutoff
        if not allowNewEntry:
            tradeMgt.CancelAllEntryOrders(activeEntryOrder = activeEntryOrder, 
                                          batchStart       = batchStart, 
                                          lastSignal       = lastSignals, 
                                          entryWinner      = entryWinner, 
                                          signalKeys       = signals)
        
        # Forced EOD liquidation trigger
        if currentTime >= forceLiqTime:
            for sk in signals:
                tradeMgt.ManageEODLiquidation(signalKey       = sk, 
                                              inTrade         = inTrade, 
                                              tradeSignalDict = tradeSignalDict, 
                                              exitOrderId     = exitOrderId, 
                                              exitInProgress  = exitInProgress, 
                                              entryFillPrice  = entryFillPrice)
                
        # Profit taking + stop loss + cleanup
        tradeMgt.ManageProfitTaking('callBuy', inTrade, stopArmed, entryFillPrice, tradeSignalDict, exitOrderId,
                                    exitInProgress, optionPrices, profitTakingPerc=profitTakingPerc, 
                                    exitThreshold = exitButterflyCallBuy, multiplier = multiplier)
        tradeMgt.ManageProfitTaking('callSell', inTrade, stopArmed, entryFillPrice, tradeSignalDict, exitOrderId,
                                    exitInProgress, optionPrices, profitTakingPerc=profitTakingPerc, 
                                    exitThreshold = exitButterflyCallSell, multiplier = multiplier)
        tradeMgt.ManageProfitTaking('putBuy', inTrade, stopArmed, entryFillPrice, tradeSignalDict, exitOrderId,
                                    exitInProgress, optionPrices, profitTakingPerc=profitTakingPerc, 
                                    exitThreshold = exitButterflyPutBuy, multiplier = multiplier)
        tradeMgt.ManageProfitTaking('putSell', inTrade, stopArmed, entryFillPrice, tradeSignalDict, exitOrderId,
                                    exitInProgress, optionPrices, profitTakingPerc=profitTakingPerc, 
                                    exitThreshold = exitButterflyPutSell, multiplier = multiplier)

        tradeMgt.ManageStopLoss('callBuy', inTrade, stopArmed, stopLossPrice, entryFillPrice, tradeSignalDict, 
                                exitOrderId, exitInProgress)
        tradeMgt.ManageStopLoss('callSell', inTrade, stopArmed, stopLossPrice, entryFillPrice, tradeSignalDict, 
                                exitOrderId, exitInProgress)
        tradeMgt.ManageStopLoss('putBuy', inTrade, stopArmed, stopLossPrice, entryFillPrice, tradeSignalDict, 
                                exitOrderId, exitInProgress)
        tradeMgt.ManageStopLoss('putSell', inTrade, stopArmed, stopLossPrice, entryFillPrice, tradeSignalDict, 
                                exitOrderId, exitInProgress)

        # Settle any exit orders submitted on this row
        tws.SettleSubmittedOrder()

        for sk in signals:
            tradeMgt.ManageExitCleanup(sk,
                                       inTrade,
                                       exitOrderId,
                                       exitInProgress,
                                       stopArmed,
                                       entryFillPrice,
                                       stopLossPrice,
                                       tradeSignalDict,
                                       entryWinner,
                                       activeEntryOrder,
                                       lastSignals,
                                       batchStart )

        totalRealisedPnl = float(tracker.realisedCumPnl)

        # Detailed per-bar state logging like the old trade_butterfly debug rows
        for sk in signals:
            stateRows.append(StateRowContinuous(
                signalKey        = sk,
                ts               = currentTS,
                tradeMgt         = tradeMgt,
                optionPrices     = optionPrices,
                valuationMap     = valuationMap,
                inTrade          = inTrade,
                tradeSignalDict  = tradeSignalDict,
                entryFillPrice   = entryFillPrice,
                stopLossPrice    = stopLossPrice,
                totalRealisedPnl = totalRealisedPnl,
                multiplier       = multiplier,
                commission       = commission,
                profitTakingPerc = profitTakingPerc
            ))

    dayEndRealised = float(tracker.realisedCumPnl)
    summaryRows.append({'date': d,
                        'daily realised pnl': dayEndRealised - dayStartRealised,
                        'cum realised pnl': dayEndRealised })
#**************************************************************************************
#======================================================================================

# ======================================================================================
# **************************************************************************************
# Outputs
tradeLogDf  = tracker.ToDataframe()
marketLogDf = pd.DataFrame(tracker.surfRows, columns = tracker.surfCols)
stateLogDf  = pd.DataFrame(stateRows)
summaryDf   = pd.DataFrame(summaryRows)

# Optional file outputs
outputBase = '/home/lun/Desktop/Folder 2/AlgoTradingPython/Test/Backtest Results'
os.makedirs(outputBase, exist_ok = True)

tradeLogDf.to_csv(outputBase + f'/BacktestTradeLog_adapter_{tradeDate}.csv', index = False)
marketLogDf.to_csv(outputBase + f'/BacktestMarketSurface_adapter_{tradeDate}.csv', index = False)
stateLogDf.to_csv(outputBase + f'/BacktestStateLog_adapter_{tradeDate}.csv', index = False)
summaryDf.to_csv(outputBase + f'/BacktestSummary_adapter_{tradeDate}.csv', index = False)
# **************************************************************************************
# ======================================================================================




































