# Set directory
import os
os.chdir('/home/lun/Desktop/Folder 2/AlgoTradingPython')
directory = os.getcwd() 

from UDF.TWSWrapper.twsWrapper   import twsWrapper
from UDF.Contract.MakeContract   import MakeContract
from UDF.Data.MarketData         import MarketData
from UDF.Data.OptionChain        import OptionChain
from UDF.Orders.Orders           import Orders
from UDF.Contract.OptionContract import OptionContract
from UDF.Tools.Interpolation     import Interpolation
from UDF.Tools.GetConId          import GetConId
from UDF.CashAmount.CashAmount   import CashAmount
from UDF.TradingHours.TradingHours import TradingHours
from ibapi.contract              import Contract

# Models
from Strategy.OptionRiskNeutral.GeneralisedGamma import GeneralisedGamma
from Strategy.OptionRiskNeutral.OptionArbitrage  import OptionArbitrage
from Strategy.OptionRiskNeutral.TradeManagement  import TradeManagement
from Strategy.OptionRiskNeutral.TradeTracker     import TradeTracker

# Library
import pandas as pd
import datetime as dt
import time
import copy

#======================================================================================
#**************************************************************************************
# Config
configName       = 'configOption.xlsx'
configTWS        = pd.read_excel(os.getcwd() + '/config/' + configName, 'TWS')
configModel      = pd.read_excel(os.getcwd() + '/config/' + configName, 'Model')
configContracts  = pd.read_excel(os.getcwd() + '/config/' + configName, 'Contracts')

dayCount = 360

currentDate = dt.datetime.now().date()
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
# Initialise objects
# TWS object
tws = twsWrapper()

# Market data
mktData = MarketData()

# Create Contract
createContract = MakeContract()
twsContract    = Contract()

# Option contract
makeOptionContract = OptionContract()

# Option chain
chain = OptionChain(enableCache = True)

# Option model generalised gamma
gg = GeneralisedGamma()

# Interpolation
interp = Interpolation()

# Get conId
conId = GetConId()

# Orders
order = Orders(tws)

# Tracking
trackingOutputPath = '/home/lun/Desktop/Folder 2/AlgoTradingPython/TradeTracking/OptionRiskNeutral'
tracker = TradeTracker(trackingOutputPath, prefix = 'OptionLedger')

# Cash Amount
cashAmt = CashAmount(tws)

# Trading Hours
th = TradingHours(tws)
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
# TWS
# Login to TWS
host     = configTWS.loc[configTWS['name'] == 'host'     , 'value'].values[0]
port     = configTWS.loc[configTWS['name'] == 'port'     , 'value'].values[0]
clientId = configTWS.loc[configTWS['name'] == 'client id', 'value'].values[0]
tws.Login(host, port, clientId)
print("connected after login:", tws.isConnected())
print("host/port/clientId:", host, port, clientId, type(port), type(clientId))

# Market Data Type. 1 for live data, 4 for delayed data. 
marketDataType = configTWS.loc[configTWS['name'] == 'market data type' , 'value'].values[0]

# Account number
accNum = configTWS.loc[configTWS['name'] == 'account num' , 'value'].values[0]
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
# Model parameters
entryButterflyPutUpperThreshold  = configModel.loc[configModel['name'] == 'butterfly put upper entry', 'value'].values[0]
entryButterflyPutLowerThreshold  = configModel.loc[configModel['name'] == 'butterfly put lower entry', 'value'].values[0]
entryButterflyCallUpperThreshold = configModel.loc[configModel['name'] == 'butterfly call upper entry', 'value'].values[0]
entryButterflyCallLowerThreshold = configModel.loc[configModel['name'] == 'butterfly call lower entry', 'value'].values[0]

exitButterflyPutBuy   = configModel.loc[configModel['name'] == 'butterfly put buy exit'  , 'value'].values[0]
exitButterflyPutSell  = configModel.loc[configModel['name'] == 'butterfly put sell exit' , 'value'].values[0]
exitButterflyCallBuy  = configModel.loc[configModel['name'] == 'butterfly call buy exit' , 'value'].values[0]
exitButterflyCallSell = configModel.loc[configModel['name'] == 'butterfly call sell exit', 'value'].values[0]

stopLossPerc     = configModel.loc[configModel['name'] == 'stop loss pnl'    , 'value'].values[0]
profitTakingPerc = configModel.loc[configModel['name'] == 'profit taking pnl', 'value'].values[0]

callCashAlloc = configModel.loc[configModel['name'] == 'call cash perc', 'value'].values[0]
putCashAlloc  = configModel.loc[configModel['name'] == 'put cash perc' , 'value'].values[0]

calibrationTimeDelay = configModel.loc[configModel['name'] == 'calibration time delay(min)', 'value'].values[0]
noNewEntryTime       = configModel.loc[configModel['name'] == 'no new entry (min)'         , 'value'].values[0]
forceLiquidTime      = configModel.loc[configModel['name'] == 'force liquidation (min)'    , 'value'].values[0]

numStrikes = configModel.loc[configModel['name'] == 'num strikes', 'value'].values[0]

optionExpiry = configModel.loc[configModel['name'] == 'option expiry', 'value'].values[0]
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
# Create contract
contracts = createContract.contractObjectList(configContracts)

# Futures contract
underlyingSymbol  = list(contracts.keys())[0]
underlyingContract = contracts[underlyingSymbol]
underlyingExpiry = str(configContracts.iloc[0, configContracts.columns.get_loc('LastTradeDateOrContractMonth')])

# SOFR contract 1
sofr1Symbol = list(contracts.keys())[1]
sofr1Contract = contracts[sofr1Symbol]

sofr2Symbol = list(contracts.keys())[2]
sofr2Contract = contracts[sofr2Symbol]
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
# Option contract set up
# ES Futures

optSymbol       = 'SPY'
optSecType      = 'OPT'
optCurrency     = 'USD'
optExchange     = 'SMART'
optExpiry       = str(int(optionExpiry))
optTradingClass = 'SPY'
optMultiplier   = str(100) 
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
# Trading
# While loop to wait until the market open

# Get the open and close time (liquid hours) and convert to Sydney time
openDTLocal, closeDTLocal, exchangeTZ = th.GetLocalOpenClosedDT(underlyingContract, useLiquid = True)
tradingHours, liquidHours, tz = th.GetTradingHours(underlyingContract)

if openDTLocal is None:
    raise RuntimeError("Market is closed today")

marketOpenTime  = openDTLocal.time()
marketCloseTime = closeDTLocal.time()

# Wait until market open (Sydney time)
while True:
    nowDT = dt.datetime.now(th.localTimeZone)
    if nowDT >= openDTLocal:
        break
    time.sleep(600)
        
# Calibrate model 
calibrationTime = openDTLocal + dt.timedelta(minutes=calibrationTimeDelay)
while True:
    currentTime = dt.datetime.now(th.localTimeZone)
    if currentTime < calibrationTime:
        time.sleep(8)
    else:
        # Get market data
        # Futures price
        try:
            underlyingPrice = mktData.GetStockPrice(tws, underlyingSymbol, underlyingContract, marketDataType)
            if underlyingPrice <= 0:
                time.sleep(8.0)
                continue
                raise ValueError('Invalid Price')
        except TimeoutError:
            time.sleep(8.0)
            continue
        
        # List of available strikes
        strikes, expiries, meta = chain.GetATMStrikeBand(tws, 
                                                         underlyingContract = underlyingContract,
                                                         underlyingSymbol   = optSymbol,
                                                         futuresPrice       = underlyingPrice,
                                                         includeExpiries    = [optExpiry],
                                                         fopExchange        = optExchange,
                                                         underlyingSecType  = 'STK', 
                                                         tradingClass       = optTradingClass, 
                                                         multiplier         = optMultiplier, 
                                                         numAroundATM       = 10)

        atmStrike = min(strikes, key = lambda k : abs(k - futuresPrice))
        atmStrikeIndex = strikes.index(atmStrike)
        
        # Select strikes for calibration. 10 on each side put/call inclusive
        putStrikes  = [strikes[atmStrikeIndex - i] for i in range(int(numStrikes))]
        callStrikes = [strikes[atmStrikeIndex + i] for i in range(int(numStrikes))]
        combineStrikes = sorted(list(set(putStrikes + callStrikes)))
        
        # Create options contracts
        optionContracts = {}
        for k in combineStrikes:
            k = str(int(k))
            optionContracts[f'put_{k}'] = copy.deepcopy(makeOptionContract.contract(twsContract, optSymbol, optSecType, 
                                                                                    optCurrency, optExchange, 'P', k,
                                                                                    optExpiry, optTradingClass,
                                                                                    optMultiplier))
            
            optionContracts[f'call_{k}'] = copy.deepcopy(makeOptionContract.contract(twsContract, optSymbol, optSecType, 
                                                                                     optCurrency, optExchange, 'C', k,
                                                                                     optExpiry, optTradingClass,
                                                                                     optMultiplier))
        optionContracts, failed = tws.qualifyContracts(optionContracts, timeout = 5.0)
        
        # Get option prices
        mktData.GetOptionBidAsk(tws, optionContracts, marketDataType, cancelAfter = False)
        strikeList     = []
        bidPrice       = []
        askPrice       = []
        optionTypeList = []
        for k in optionContracts.keys():
            bid = tws.mktDataBid.get(k, 0.0)
            ask = tws.mktDataAsk.get(k, 0.0)
            
            optTypeStrike = k.split('_')
            optType   = optTypeStrike[0]
            optStrike = float(optTypeStrike[1])
            
            if optType == 'call' and optStrike > underlyingPrice:
                strikeList.append(optStrike)
                bidPrice.append(bid)
                askPrice.append(ask)
                optionTypeList.append('call')
            elif optType == 'put' and optStrike < underlyingPrice:
                strikeList.append(optStrike)
                bidPrice.append(bid)
                askPrice.append(ask)
                optionTypeList.append('put')
        
        # Expiry
        expiry = (dt.datetime.strptime(optExpiry, '%Y%m%d').date() - currentDate).days / dayCount
        
        # Interest rate
        try:
            sofr1Price = (100 - mktData.GetFuturesLast(tws, sofr1Symbol, sofr1Contract, marketDataType)) / 100.0
        except TimeoutError:
            sofr1Price = 0.0
        sofr1Exp   = mktData.GetExpirationDate(tws, sofr1Contract)
        sofr1Exp   = dt.datetime.strptime(sofr1Exp, '%Y%m%d').date()
        sofr1Exp   = (sofr1Exp - currentDate).days / dayCount
        
        try:
            sofr2Price = (100 - mktData.GetFuturesLast(tws, sofr2Symbol, sofr2Contract, marketDataType)) / 100.0
        except TimeoutError:
            sofr2Price = 0.0
        sofr2Exp   = mktData.GetExpirationDate(tws, sofr2Contract)
        sofr2Exp   = dt.datetime.strptime(sofr2Exp, '%Y%m%d').date()
        sofr2Exp   = (sofr2Exp - currentDate).days / dayCount
        
        if sofr1Price == 0.0 and sofr2Price == 0.0:
            intRate = 0.0
        elif sofr1Price == 0.0 and sofr2Price != 0.0:
            intRate = sofr2Price
        elif sofr1Price != 0.0 and sofr2Price == 0.0:
            intRate = sofr1Price
        else:
            intRate = interp.Linear(sofr1Price, sofr2Price, sofr1Exp, sofr2Exp, expiry)
        
        # Calibrate model
        xiBid, alphaBid, resBid = gg.Calibrate(bidPrice, underlyingPrice, strikeList, expiry, intRate, optionTypeList)
        xiAsk, alphaAsk, resAsk = gg.Calibrate(askPrice, underlyingPrice, strikeList, expiry, intRate, optionTypeList) 
        
        # If calibration successful, then break
        if (gg.CalibrationSuccess(xiBid, alphaBid, resBid) and gg.CalibrationSuccess(xiAsk, alphaAsk, resAsk)):
            break
        else:
            time.sleep(10.0)
            continue
    
# Trading
tradeMgt = TradeManagement(tws, optionContracts, tracker)
optionPrices = pd.DataFrame(columns=['mkt bid', 'mkt ask', 'mkt mid', 'model bid', 'model ask'], 
                            index=pd.MultiIndex.from_tuples([], names=['type', 'strike']))
optArb = OptionArbitrage(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 
                         entryButterflyPutUpperThreshold, 
                         entryButterflyPutLowerThreshold, 
                         entryButterflyCallUpperThreshold, 
                         entryButterflyCallLowerThreshold, expiry, intRate)

signals          = ['callBuy', 'callSell', 'putBuy', 'putSell']
inTrade          = {s : False for s in signals} # Position tracking
activeEntryOrder = {s : []    for s in signals}    # Track all active orders
entryWinner      = {s : None  for s in signals}  # Store the winner (filled entry order) 
batchStart       = {s : None  for s in signals}  # when we started trying to fill for this signal
lastSignals      = {s : None  for s in signals } # remember last signal signature per bucket

entryFillPrice   = {s : None  for s in signals}
stopLossPrice    = {s : None  for s in signals}
stopArmed        = {s : False for s in signals}
tradeSignalDict  = {s : None  for s in signals}
exitOrderId      = {s : None  for s in signals}
exitInProgress   = {s : False for s in signals}

# Cash Checking
lastAcctCheckTs   = 0.0
acctCheckEverySec = 5.0
usdCash           = 0.0
usdAvail          = 0.0

# Set time
noNewEntryDT = closeDTLocal - dt.timedelta(minutes = noNewEntryTime)
forceLiqDT   = closeDTLocal - dt.timedelta(minutes = forceLiquidTime)
eodEntryCancelDone = False
eodForceTriggered  = False

# Tracking
tracker.InitMarketSurface(optionContracts)

while True:
    # Time now. Use to break the while loop.
    nowDT          = dt.datetime.now(th.localTimeZone)
    allowNewEntry  = nowDT < noNewEntryDT
    forceLiquidate = nowDT >= forceLiqDT
    
    # Data streaming
        # Futures last price
    futuresPrice = tws.mktDataLast.get(underlyingSymbol)
    '''
    if futuresPrice is None or futuresPrice <= 0:
        time.sleep(0.2)
        continue
    '''
    
        # Options bid ask
    surfRow = tracker.SurfaceNewRow(futuresPrice)
    for k in optionContracts.keys():
        bid = tws.mktDataBid.get(k, 0.0)
        ask = tws.mktDataAsk.get(k, 0.0)
        mid = 0.5 * (bid + ask) if (bid > 0 and ask > 0) else 0.0
        optType, strike = k.split('_')
        
        # Model prices
        modelPriceBid = gg.OptionPrice(futuresPrice, float(strike), expiry, intRate, xiBid, alphaBid, optType)
        modelPriceAsk = gg.OptionPrice(futuresPrice, float(strike), expiry, intRate, xiAsk, alphaAsk, optType)
        
        optionPrices.loc[(optType, strike), ['mkt bid', 'mkt ask', 'mkt mid', 'model bid'  , 'model ask']] = \
                                            [bid      , ask      , mid      , modelPriceBid, modelPriceAsk]
        
        # collect into surface row
        tracker.SurfaceSet(surfRow, k, bid, ask, modelPriceBid, modelPriceAsk)
    tracker.SurfaceAppendRow(surfRow)
    
    # Model Signals generation
    optArb.ParamSetUp(optionPrices, futuresPrice, expiry, intRate)
    res = optArb.Arbitrage()
    butterflyCallBuy, butterflyCallSell, butterflyPutBuy, butterflyPutSell = res['skew']['butterfly']
    
    # Tracking
    signalMap = {"callBuy"  : butterflyCallBuy,
                 "callSell" : butterflyCallSell,
                 "putBuy"   : butterflyPutBuy,
                 "putSell"  : butterflyPutSell,}
    for sk, sig in signalMap.items():
        sigTrade = tradeSignalDict.get(sk)
        if isinstance(sigTrade, dict) and sigTrade:
            sigUse = sigTrade
        else:
            # If flat, value the current signal (if any)
            if not isinstance(sig, dict) or not sig:
                continue
            sigUse = sig
            
        mktQ = tradeMgt.ButterflyQuote(sigUse)
        modQ = tradeMgt.ButterflyModelQuote(sigUse, optionPrices)
        if mktQ is None or modQ is None:
            continue
    
        mktBid, mktAsk, mktMid = mktQ
        modBid, modAsk, modMid = modQ
        diff = (mktMid - modMid) if (mktMid is not None and modMid is not None) else None
    
        tracker.OnMarket(signalKey    = sk,
                         futuresPrice = futuresPrice,
                         mktBid       = mktBid,
                         mktAsk       = mktAsk,
                         mktMid       = mktMid,
                         modelBid     = modBid,
                         modelAsk     = modAsk,
                         modelMid     = modMid,
                         diff         = diff)
    
    # Place order
    if allowNewEntry:
        entrySignalMap = {'callBuy':  butterflyCallBuy,
                          'callSell': butterflyCallSell,
                          'putBuy':   butterflyPutBuy,
                          'putSell':  butterflyPutSell,}
    
        familyMap = {'callBuy':  ['callSell'],
                     'callSell': ['callBuy'],
                     'putBuy':   ['putSell'],
                     'putSell':  ['putBuy']}
    
        for sk, sig in entrySignalMap.items():
            siblingBusy = any(inTrade[s] or len(activeEntryOrder[s]) > 0 or exitInProgress[s] for s in familyMap[sk])
            if siblingBusy:
                continue
    
            hasSignal = isinstance(sig, dict) and bool(sig)
            hasTrackedEntry = len(activeEntryOrder.get(sk, [])) > 0
    
            if not hasSignal and not hasTrackedEntry:
                continue
    
            sigUse = sig if hasSignal else {}
    
            qty = 1
            tradeMgt.ManageEntry(sk, sigUse, inTrade, activeEntryOrder, entryWinner, batchStart,
                                 lastSignals, entryFillPrice, stopLossPrice, stopArmed,
                                 tradeSignalDict, exitInProgress,
                                 numContract = qty, ttlSeconds = 2.0,
                                 stopLossPerc = stopLossPerc)
    
    # Cancel all Entry
    if (not allowNewEntry) and (not eodEntryCancelDone):
        tradeMgt.CancelAllEntryOrders(activeEntryOrder = activeEntryOrder, 
                                      batchStart       = batchStart, 
                                      lastSignal       = lastSignals, 
                                      entryWinner      = entryWinner, 
                                      signalKeys       = signals)
        eodEntryCancelDone = True
        
    if forceLiquidate and (not eodForceTriggered):
        tradeMgt.CancelAllEntryOrders(activeEntryOrder = activeEntryOrder, 
                                      batchStart       = batchStart, 
                                      lastSignal       = lastSignals, 
                                      entryWinner      = entryWinner, 
                                      signalKeys       = signals)
        eodForceTriggered = True
    
    # Force liquidation EOD
    if forceLiquidate:
        for sk in signals:
            if not inTrade.get(sk, False):
                continue
            if exitInProgress.get(sk, False):
                continue
            
            sigTrade = tradeSignalDict.get(sk)
            if not isinstance(sigTrade, dict) or not sigTrade:
                continue
            
            tradeMgt.ManageEODLiquidation(signalKey       = sk, 
                                          inTrade         = inTrade, 
                                          tradeSignalDict = tradeSignalDict, 
                                          exitOrderId     = exitOrderId, 
                                          exitInProgress  = exitInProgress, 
                                          entryFillPrice  = entryFillPrice)
            
    # Profit taking
    tradeMgt.ManageProfitTaking('callBuy', inTrade, stopArmed, entryFillPrice, tradeSignalDict, exitOrderId,
                                           exitInProgress, optionPrices,
                                           profitTakingPerc = profitTakingPerc, exitThreshold = exitButterflyCallBuy, 
                                           multiplier = int(optMultiplier))

    tradeMgt.ManageProfitTaking('callSell', inTrade, stopArmed, entryFillPrice, tradeSignalDict, exitOrderId,
                                            exitInProgress, optionPrices,
                                            profitTakingPerc = profitTakingPerc, exitThreshold = exitButterflyCallSell, 
                                            multiplier = int(optMultiplier))

    tradeMgt.ManageProfitTaking('putBuy', inTrade, stopArmed, entryFillPrice, tradeSignalDict, exitOrderId,
                                          exitInProgress, optionPrices,
                                          profitTakingPerc = profitTakingPerc, exitThreshold = exitButterflyPutBuy, 
                                          multiplier = int(optMultiplier))

    tradeMgt.ManageProfitTaking('putSell', inTrade, stopArmed, entryFillPrice, tradeSignalDict, exitOrderId,
                                           exitInProgress, optionPrices,
                                           profitTakingPerc = profitTakingPerc, exitThreshold = exitButterflyPutSell, 
                                           multiplier = int(optMultiplier))
    
    # Stop loss
    tradeMgt.ManageStopLoss('callBuy', inTrade, stopArmed, stopLossPrice, entryFillPrice, tradeSignalDict, 
                                       exitOrderId, exitInProgress)
    tradeMgt.ManageExitCleanup('callBuy', inTrade, exitOrderId, exitInProgress, stopArmed, entryFillPrice, 
                                          stopLossPrice, tradeSignalDict, entryWinner, activeEntryOrder, lastSignals, 
                                          batchStart)
    
    tradeMgt.ManageStopLoss('callSell', inTrade, stopArmed, stopLossPrice, entryFillPrice, tradeSignalDict, 
                                        exitOrderId, exitInProgress)
    tradeMgt.ManageExitCleanup('callSell', inTrade, exitOrderId, exitInProgress, stopArmed, entryFillPrice, 
                                           stopLossPrice, tradeSignalDict, entryWinner, activeEntryOrder, lastSignals, 
                                           batchStart)
    
    tradeMgt.ManageStopLoss('putBuy', inTrade, stopArmed, stopLossPrice, entryFillPrice, tradeSignalDict, 
                                      exitOrderId, exitInProgress)
    tradeMgt.ManageExitCleanup('putBuy', inTrade, exitOrderId, exitInProgress, stopArmed, entryFillPrice, 
                                         stopLossPrice, tradeSignalDict, entryWinner, activeEntryOrder, lastSignals, 
                                         batchStart)
    
    tradeMgt.ManageStopLoss('putSell', inTrade, stopArmed, stopLossPrice, entryFillPrice, tradeSignalDict, 
                                       exitOrderId, exitInProgress)
    tradeMgt.ManageExitCleanup('putSell', inTrade, exitOrderId, exitInProgress, stopArmed, entryFillPrice, 
                                          stopLossPrice, tradeSignalDict, entryWinner, activeEntryOrder, lastSignals, 
                                          batchStart)
    
    # slight delay
    time.sleep(0.2)
    
    #Break the loop after force liquidity time has passed. 
    if dt.datetime.now(th.localTimeZone) >= forceLiqDT:
        break

# -------------------------------------------------------------------
# Post-close liquidation drain loop: keep managing exits until flat
# -------------------------------------------------------------------
drainDeadline = dt.datetime.now(th.localTimeZone) + dt.timedelta(minutes=10)

while dt.datetime.now(th.localTimeZone) < drainDeadline:

    # keep canceling any leftover entry orders
    tradeMgt.CancelAllEntryOrders(activeEntryOrder=activeEntryOrder,
                                  batchStart=batchStart,
                                  lastSignal=lastSignals,
                                  entryWinner=entryWinner,
                                  signalKeys=signals)

    # trigger EOD liquidation for anything still open
    for sk in signals:
        if inTrade.get(sk, False) and not exitInProgress.get(sk, False):
            tradeMgt.ManageEODLiquidation(signalKey=sk,
                                          inTrade=inTrade,
                                          tradeSignalDict=tradeSignalDict,
                                          exitOrderId=exitOrderId,
                                          exitInProgress=exitInProgress,
                                          entryFillPrice=entryFillPrice)

    # keep cleaning up exits
    for sk in signals:
        tradeMgt.ManageExitCleanup(sk, inTrade, exitOrderId, exitInProgress, stopArmed,
                                   entryFillPrice, stopLossPrice, tradeSignalDict,
                                   entryWinner, activeEntryOrder, lastSignals, batchStart)

    # stop early only when everything is flat and no exit order is tracked
    if all(not inTrade.get(sk, False) for sk in signals) and \
       all(not exitInProgress.get(sk, False) for sk in signals) and \
       all(exitOrderId.get(sk) is None for sk in signals):
        break

    time.sleep(0.5)
    
tracker.Flush(suffix=f"ES_{dt.datetime.now():%Y%m%d}", toExcel = False)
tracker.FlushMarketSurface(toExcel = False)
#**************************************************************************************
#======================================================================================

    
