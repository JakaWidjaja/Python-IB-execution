from UDF.Orders.Orders       import Orders
from UDF.Orders.OrderManager import OrderManager
import time

class TradeManagement:
    def __init__(self, tws, optionContracts, tracker = None):
        self.tws             = tws
        self.optionContracts = optionContracts
        self.tracker         = tracker
        
        self.order = Orders(self.tws)
        
        self.ordManager = OrderManager(self.tws)
        tws.ordManager  = self.ordManager
    
    def FamilyKeys(self, signalKey):
        familyMap = {'callBuy':  ('callBuy', 'callSell'),
                     'callSell': ('callBuy', 'callSell'),
                     'putBuy':   ('putBuy', 'putSell'),
                     'putSell':  ('putBuy', 'putSell')}
        
        return familyMap.get(signalKey, (signalKey,))
    
    def FamilyBusy(self, signalKey, inTrade, activeEntryOrder, exitInProgress):
        family = self.FamilyKeys(signalKey)

        for sk in family:
            if sk == signalKey:
                continue
    
            if inTrade.get(sk, False):
                return True
    
            if exitInProgress.get(sk, False):
                return True
    
            # hard local lock: any tracked sibling entry means busy
            if len(activeEntryOrder.get(sk, [])) > 0:
                return True
    
        return False
    
    def FindFilledEntryOrder(self, signalKey, excludeOid=None):
        found = []
    
        for oid, o in self.ordManager.orders.items():
            try:
                meta = o.meta or {}
            except Exception:
                meta = {}
    
            if meta.get("signal") != signalKey:
                continue
            if meta.get("strategy") != "skew butterfly":
                continue
            if "reason" in meta:
                continue
    
            if excludeOid is not None and oid == excludeOid:
                continue
    
            if self.ordManager.Filled(oid):
                found.append(oid)
    
        return max(found) if found else None

    def ManageEntry(self, signalKey, signalDict, inTrade, activeEntryOrder, entryWinner, batchStart, lastSignal,
                entryFillPrice, stopLossPrice, stopArmed, tradeSignalDict, exitInProgress,
                numContract=1, ttlSeconds=5.0, stopLossPerc=0.30):
        """
        Manage one entry bucket (e.g. callBuy, callSell, putBuy, putSell).
    
        State machine:
        1. If a live trade already exists but stop is not armed yet, try to enrich fill data.
        2. If a tracked entry order has filled, promote it to a live trade.
        3. If the tracked order was lost, recover the filled entry from OrderManager.
        4. If an entry order is still working, wait or cancel on TTL.
        5. Only then consider placing a NEW entry order.
        6. Block new entries if the sibling signal in the same family is busy.
    
        Notes:
        - Entry orders are registered without a "reason" in meta.
        - Exit orders are registered with a "reason" in meta.
        - We use that distinction inside self.FindFilledEntryOrder(signalKey).
        """
    
        # ------------------------------------------------------------
        # Helper: signature of the spread structure
        # Excludes price, so the same structure is not re-submitted
        # over and over when market quotes move slightly.
        # ------------------------------------------------------------
        def SigSignature(d):
            return (d.get('direction'),
                    d.get('long call 1'), d.get('short call 1'),
                    d.get('long call 2'), d.get('short call 2'),
                    d.get('long put 1'),  d.get('short put 1'),
                    d.get('long put 2'),  d.get('short put 2'))
    
        # ------------------------------------------------------------
        # Helper: tracker hook for filled entry
        # ------------------------------------------------------------
        def TrackEntryFill(sigForTrade, winnerOid, direction):
            if self.tracker is None:
                return
    
            try:
                mktBid, mktAsk, mktMid = self.ButterflyQuote(sigForTrade) or (None, None, None)
            except Exception:
                mktBid = mktAsk = mktMid = None
    
            try:
                legQuotes = self.ButterflyLegQuotes(sigForTrade)
                self.tracker.OnEntryFilled(signalKey    = signalKey,
                                           entryOrderId = winnerOid,
                                           direction    = direction,
                                           qty          = int(numContract),
                                           entryFill    = entryFillPrice.get(signalKey),
                                           futuresPrice = self.tws.mktDataLast.get("ES", None),
                                           mktBid       = mktBid,
                                           mktAsk       = mktAsk,
                                           mktMid       = mktMid,
                                           modelBid     = None,
                                           modelAsk     = None,
                                           modelMid     = None,
                                           diff         = None,
                                           legQuotes    = legQuotes)
            except Exception as e:
                print(f"TRACKER WARN {signalKey}: {e}")
    
        # ------------------------------------------------------------
        # Helper: promote a filled entry order into a live trade
        #
        # Returns True if promotion completed or partially completed.
        # "Partially completed" means:
        #   - inTrade=True
        #   - but avgFillPrice not available yet
        #   - so stopArmed remains False for now
        # ------------------------------------------------------------
        def PromoteFilledOrder(winnerOid, signalDictArg=None):
            o = self.ordManager.orders.get(winnerOid)
            if o is None:
                print(f"PROMOTE FAIL {signalKey}: missing order object for oid={winnerOid}")
                return False
        
            # Prefer the current signalDict if present; otherwise recover from meta
            meta_sig = None
            try:
                meta_sig = (o.meta or {}).get("signalDict")
            except Exception:
                meta_sig = None
        
            if isinstance(signalDictArg, dict) and signalDictArg:
                sigForTrade = dict(signalDictArg)
            elif isinstance(meta_sig, dict) and meta_sig:
                sigForTrade = dict(meta_sig)
            else:
                print(f"PROMOTE FAIL {signalKey}: missing signalDict")
                return False
        
            direction = str(sigForTrade.get("direction", "")).upper()
            if direction not in ("BUY", "SELL"):
                print(f"PROMOTE FAIL {signalKey}: invalid direction={direction}")
                return False
        
            # avgFillPrice may lag even after a fill
            avgFillRaw = getattr(o, "avgFillPrice", None)
            avgFill = None
            try:
                if avgFillRaw is not None:
                    avgFill = float(avgFillRaw)
            except Exception:
                avgFill = None
        
            # NEW: detect whether this is the first promotion
            firstPromotion = (entryWinner.get(signalKey) is None)
        
            # Mark live trade immediately so the system does not think it is flat
            entryWinner[signalKey]                    = winnerOid
            tradeSignalDict[signalKey]                = dict(sigForTrade)
            tradeSignalDict[signalKey]["numContract"] = int(numContract)
            inTrade[signalKey]                        = True
        
            # Only arm stop once avg fill is available
            if avgFill is not None and avgFill > 0.0:
                entryFillPrice[signalKey] = avgFill
                stopLossPrice[signalKey]  = self.CalcStopFromFill(direction, avgFill, stopLossPerc)
                stopArmed[signalKey]      = True
                print(f"PROMOTE OK {signalKey}: oid={winnerOid}, avgFill={avgFill}")
            else:
                entryFillPrice[signalKey] = None
                stopLossPrice[signalKey]  = None
                stopArmed[signalKey]      = False
                print(f"PROMOTE WARN {signalKey}: oid={winnerOid}, filled but avgFill unavailable")
        
            # Keep the winning entry id tracked
            activeEntryOrder[signalKey] = [winnerOid]
            batchStart[signalKey] = None
        
            # NEW: only track once
            if firstPromotion:
                TrackEntryFill(sigForTrade, winnerOid, direction)
        
            return True
    
        now = time.time()
    
        # ------------------------------------------------------------
        # STEP 0: if trade is already live, optionally enrich missing fill info
        #
        # This is important because avgFillPrice may not exist when the
        # fill is first promoted. Without this block, stopArmed could stay
        # False forever.
        # ------------------------------------------------------------
        if inTrade.get(signalKey, False):
            if not stopArmed.get(signalKey, False):
                winnerOid = entryWinner.get(signalKey)
    
                if winnerOid is None:
                    winnerOid = self.FindFilledEntryOrder(signalKey)
    
                if winnerOid is not None:
                    o = self.ordManager.orders.get(winnerOid)
                    sig = tradeSignalDict.get(signalKey)
    
                    if o is not None and isinstance(sig, dict) and sig:
                        avgFillRaw = getattr(o, "avgFillPrice", None)
                        avgFill = None
                        try:
                            if avgFillRaw is not None:
                                avgFill = float(avgFillRaw)
                        except Exception:
                            avgFill = None
    
                        direction = str(sig.get("direction", "")).upper()
                        if avgFill is not None and avgFill > 0.0 and direction in ("BUY", "SELL"):
                            entryWinner[signalKey]    = winnerOid
                            entryFillPrice[signalKey] = avgFill
                            stopLossPrice[signalKey]  = self.CalcStopFromFill(direction, avgFill, stopLossPerc)
                            stopArmed[signalKey]      = True
                            print(f"ENRICH OK {signalKey}: oid={winnerOid}, avgFill={avgFill}")
    
            return
    
        # ------------------------------------------------------------
        # STEP 1: promote a filled tracked order first
        # ------------------------------------------------------------
        currentIds = list(activeEntryOrder.get(signalKey, []))
    
        filledTracked = [oid for oid in currentIds if self.ordManager.Filled(oid)]
        if filledTracked:
            winnerOid = filledTracked[0]
            if PromoteFilledOrder(winnerOid, signalDict):
                return
    
        # ------------------------------------------------------------
        # STEP 2: recover a filled entry if the tracked list lost it
        # ------------------------------------------------------------
        if exitInProgress.get(signalKey, False):
            return
        
        # Only recover while an entry attempt is still in progress / recently active
        if batchStart.get(signalKey) is not None:
            recoveredOid = self.FindFilledEntryOrder(signalKey, excludeOid=entryWinner.get(signalKey))
            if recoveredOid is not None and recoveredOid not in currentIds:
                print(f"RECOVER {signalKey}: recovered entry oid={recoveredOid}")
                if PromoteFilledOrder(recoveredOid, signalDict):
                    return
    
        # ------------------------------------------------------------
        # STEP 3: clean THIS signal's tracked list
        #
        # Keep filled orders even if Done=True so they remain promotable
        # on the next pass.
        # ------------------------------------------------------------
        activeEntryOrder[signalKey] = [oid for oid in activeEntryOrder.get(signalKey, [])
                                       if (not self.ordManager.Done(oid)) or self.ordManager.Filled(oid)]
    
        # ------------------------------------------------------------
        # STEP 4: if THIS signal still has a working entry order,
        # do not place another one
        # ------------------------------------------------------------
        working = [oid for oid in activeEntryOrder[signalKey] if self.ordManager.Working(oid)]
    
        if working:
            if batchStart[signalKey] is None:
                batchStart[signalKey] = now
    
            # Cancel stale working entry after TTL
            if (now - batchStart[signalKey]) >= ttlSeconds:
                print(f"TTL CANCEL {signalKey}: {working}")
                for oid in list(activeEntryOrder[signalKey]):
                    if self.ordManager.Working(oid):
                        self.ordManager.Cancel(oid)
    
                activeEntryOrder[signalKey] = []
                batchStart[signalKey] = None
    
            return
    
        # ------------------------------------------------------------
        # STEP 5: block NEW entry if sibling family is busy
        #
        # This should happen only after we finish managing this signal's
        # own tracked orders.
        # ------------------------------------------------------------
        if self.FamilyBusy(signalKey, inTrade, activeEntryOrder, exitInProgress):
            return
    
        # ------------------------------------------------------------
        # STEP 6: if there is no valid new signal, nothing to do
        # ------------------------------------------------------------
        if not isinstance(signalDict, dict) or not signalDict:
            return
    
        # ------------------------------------------------------------
        # STEP 7: do not re-submit the same structure repeatedly
        # ------------------------------------------------------------
        sig = SigSignature(signalDict)
        if sig == lastSignal[signalKey]:
            return
    
        # ------------------------------------------------------------
        # STEP 8: compute live spread quote for entry price
        #
        # BUY entry  -> pay spread ask
        # SELL entry -> receive spread bid
        # ------------------------------------------------------------
        quote = self.ButterflyQuote(signalDict)
        if quote is None:
            return
    
        spreadBid, spreadAsk, _ = quote
    
        direction = str(signalDict.get("direction", "")).upper()
        if direction == "BUY":
            lmtPrice = float(spreadAsk)
        elif direction == "SELL":
            lmtPrice = float(spreadBid)
        else:
            return
    
        if lmtPrice <= 0.0:
            return
    
        # ------------------------------------------------------------
        # STEP 9: submit new entry order
        # ------------------------------------------------------------
        orderId = self.order.ButterflyLmtOrder(self.optionContracts,
                                               signalDict,
                                               int(numContract),
                                               lmtPrice)
    
        self.ordManager.Register(orderId,
                                 meta={'strategy'  : 'skew butterfly',
                                       'signal'    : signalKey,
                                       'limit'     : lmtPrice,
                                       'signalDict': dict(signalDict),
                                       'qty'       : int(numContract)})
    
        activeEntryOrder[signalKey] = [orderId]
        lastSignal[signalKey]       = sig
        batchStart[signalKey]       = now
    
        print(f"SUBMIT ENTRY {signalKey}: orderId={orderId}, direction={direction}, lmtPrice={lmtPrice}")
                
    def ManageStopLoss(self, signalKey, inTrade, stopArmed, stopLossPrice, entryFillPrice, tradeSignalDict, 
                       exitOrderId, exitInProgress):
        '''
        Synthetic stop:
            - only activate after stopArmed[signalKey] == True (entry filled)
            - compute current butterfly mark from live bid/ask
            - if stop breached -> place exit order and set exitInProgress
        '''
        
        # No position/ no armed stop -> do nothing
        if not inTrade.get(signalKey, False):
            return
        if not stopArmed.get(signalKey, False):
            return
        if exitInProgress.get(signalKey, False):
            return
        
        sig = tradeSignalDict.get(signalKey)
        if not sig:
            return
        
        direction = str(sig.get('direction', '')).upper()
        if direction not in ('BUY', 'SELL'):
            # if long/short, then need to change it here
            return 
        
        # Need live prices for legs
        quote = self.ButterflyQuote(sig)
        if quote is None:
            return
        
        spreadBid, spreadAsk, spreadMid = quote
        stopLevel = float(stopLossPrice[signalKey])
        
        # Stop condition
        # Entry buy loses whn spread value drops
        # Entry Sell loses when spread value rises
        if direction == 'BUY':
            stopHit = (spreadBid <= stopLevel)
        else:
            stopHit = (spreadAsk >= stopLevel)
            
        if not stopHit:
            return
        
        # Trigger exit
        exitInProgress[signalKey] = True
        
        # Opposite action to flatten
        exitAction = 'SELL' if direction == 'BUY' else 'BUY'
        
        # Market order
        qty = int(sig.get("numContract", 1))
        sig2 = dict(sig)
        sig2['direction'] = exitAction
        
        if hasattr(self.order, 'ButterflyMktOrder'):
            orderId = self.order.ButterflyMktOrder(self.optionContracts, sig2, qty, exitAction)
        else:
            lmt = spreadBid if exitAction == 'SELL' else spreadAsk
            lmt = float(max(lmt, 0.01))
            sig2['limit price'] = lmt
            orderId = self.order.ButterflyLmtOrder(self.optionContracts, sig2, qty, lmt)
                
        self.ordManager.Register(orderId, meta = {'strategy'   : 'skew butterfly', 
                                                  'signal'     : signalKey, 
                                                  'reason'     : 'stop loss', 
                                                  'stop level' : stopLevel, 
                                                  'entry fill' : entryFillPrice.get(signalKey), 
                                                  'qty'        : qty})
        
        exitOrderId[signalKey] = orderId
        print(' STOP LOSS')
        
    def ManageExitCleanup(self, signalKey, inTrade, exitOrderId, exitInProgress, stopArmed, entryFillPrice, stopLossPrice, 
                          tradeSignalDict, entryWinner, activeEntryOrder, lastSignal, batchStart):
        if exitInProgress.get(signalKey) is False:
            return

        orderId = exitOrderId.get(signalKey)
        if not orderId:
            return
        
        # Tracking
        if self.ordManager.Filled(orderId):
            o = self.ordManager.orders.get(orderId)
            exitFill = None
            if o is not None:
                try:
                    exitFill = float(o.avgFillPrice)
                except (TypeError, ValueError):
                    exitFill = None
        
            exitReason = None
            try:
                exitReason = (o.meta or {}).get("reason")
            except Exception:
                exitReason = None
        
            if exitFill is not None and self.tracker is not None:
                sig = tradeSignalDict.get(signalKey)
                legQuotes = self.ButterflyLegQuotes(sig) if isinstance(sig, dict) and sig else {}
                self.tracker.OnExitFilled(signalKey      = signalKey,
                                          exitOrderId    = orderId,
                                          exitReason     = exitReason,
                                          exitFill       = exitFill,
                                          futuresPrice   = self.tws.mktDataLast.get("ES", None), 
                                          legQuotes      = legQuotes)
                exitInProgress[signalKey] = False
    
        if self.ordManager.Filled(orderId):
            # real exit fill -> clear state
            inTrade[signalKey] = False
            exitInProgress[signalKey] = False
            exitOrderId[signalKey] = None
            stopArmed[signalKey] = False
            entryFillPrice[signalKey] = None
            stopLossPrice[signalKey] = None
            tradeSignalDict[signalKey] = None
            entryWinner[signalKey] = None
            activeEntryOrder[signalKey] = []
            lastSignal[signalKey] = None
            batchStart[signalKey] = None
        
        elif self.ordManager.Done(orderId):
            # exit order is no longer working, but did NOT fill
            # clear only exit-tracking, keep live trade state
            exitInProgress[signalKey] = False
            exitOrderId[signalKey] = None
            
    def CalcStopFromFill(self, direction, entryFill, stopLossPerc):
        if direction == 'BUY':
            return entryFill * (1.0 - stopLossPerc)
        else:
            return entryFill * (1.0 + stopLossPerc)
        
    def ButterflyQuote(self, signalDict):
        
        legs = []
        def AddLeg(optType, strike, sign):
            if strike is None:
                return
            try:
                k = str(int(float(strike)))
            except Exception:
                k = str(strike)
                
            sym = f'{optType}_{k}'
            legs.append((sym, sign))
            
        AddLeg('put', signalDict.get('long put 1') , +1)
        AddLeg('put', signalDict.get('long put 2') , +1)
        AddLeg('put', signalDict.get('short put 1'), -1)
        AddLeg('put', signalDict.get('short put 2'), -1)
            
        AddLeg('call', signalDict.get('long call 1') , +1)
        AddLeg('call', signalDict.get('long call 2') , +1)
        AddLeg('call', signalDict.get('short call 1'), -1)
        AddLeg('call', signalDict.get('short call 2'), -1)
        
        if not legs:
            return None
        
        spreadBid = 0.0
        spreadAsk = 0.0
        
        for sym, sign in legs:
            bid = float(self.tws.mktDataBid.get(sym, 0.0))
            ask = float(self.tws.mktDataAsk.get(sym, 0.0))
            if bid <= 0.0 and ask <= 0.0:
                return None # missing quotes
            
            mid = (bid + ask) / 2.0 if (bid > 0.0 and ask > 0.0) else (ask if ask > 0 else bid)
            
            # Approximate Bid/Ask:
            # - To compute spreadBid (receive if SELL the spread):
            #   use bid for long legs, ask for short legs
            # - To compute spreadAsk (pay if BUY the spread):
            #   use ask for long legs, bid for short legs
            
            if sign > 0:
                spreadBid += bid
                spreadAsk += ask
            else:
                spreadBid -= ask
                spreadAsk -= bid
                
        spreadMid = (spreadBid + spreadAsk) / 2.0
        return spreadBid, spreadAsk, spreadMid
    
    def ManageProfitTaking(self, signalKey, inTrade, stopArmed, entryFillPrice, tradeSignalDict, exitOrderId, 
                           exitInProgress, optionPrices, profitTakingPerc = 0.20, exitThreshold =0.0, commision = 6.0, 
                           multiplier = 50):
        if not inTrade.get(signalKey, False):
            return
        if not stopArmed.get(signalKey, False):
            return
        if exitInProgress.get(signalKey, False):
            return
        
        sig = tradeSignalDict.get(signalKey)
        if not sig:
            return
        
        direction = str(sig.get('direction', '')).upper()
        if direction not in ('BUY', 'SELL'):
            return
        
        # Market butterfly mark
        mktQuote = self.ButterflyQuote(sig)
        if mktQuote is None:
            return
        
        mktBid, mktAsk, mktMid = mktQuote

        fill = entryFillPrice.get(signalKey)
        if fill is not None and float(fill) > 0.0:
            fill = float(fill)
            qty  = int(sig.get('numContract', 1))
            commisionTotal = float(commision) * qty
        
            if direction == 'BUY':
                exitMark = float(mktBid)   # close by selling
                pnl = (exitMark - fill) * multiplier * qty - commisionTotal
                pnlTarget = fill * profitTakingPerc * multiplier * qty
                if pnl >= pnlTarget:
                    return self.PlaceExit(signalKey, sig, direction, mktBid, mktAsk,
                                          entryFillPrice, exitOrderId, exitInProgress,
                                          reason='profit target',
                                          extra={'profitTakingPerc': float(profitTakingPerc)})
        
            else:  # SELL entry
                exitMark = float(mktAsk)   # close by buying
                pnl = (fill - exitMark) * multiplier * qty - commisionTotal
                pnlTarget = fill * profitTakingPerc * multiplier * qty
                if pnl >= pnlTarget:
                    return self.PlaceExit(signalKey, sig, direction, mktBid, mktAsk,
                                          entryFillPrice, exitOrderId, exitInProgress,
                                          reason='profit target',
                                          extra={'profitTakingPerc': float(profitTakingPerc)})
                
        ggQuote = self.ButterflyModelQuote(sig, optionPrices)
        if ggQuote is None:
            return
        
        ggBid, ggAsk, _ = ggQuote
        
        if direction == 'BUY':
            # To close a long butterfly, you SELL it -> use bid side
            diff = float(mktBid) - float(ggBid)
        else:
            # To close a short butterfly, you BUY it back -> use ask side
            diff = float(mktAsk) - float(ggAsk)
        
        if diff <= float(exitThreshold):
            return self.PlaceExit(signalKey, sig, direction, mktBid, mktAsk,
                                  entryFillPrice, exitOrderId, exitInProgress,
                                  reason='model exit',
                                  extra={'diff': diff, 'exitThreshold': float(exitThreshold)})
        
    def PlaceExit(self, signalKey, sig, direction, spreadBid, spreadAsk,
              entryFillPrice, exitOrderId, exitInProgress,
              reason='exit', extra=None, forceMkt=False):

        exitInProgress[signalKey] = True
        exitAction = 'SELL' if direction == 'BUY' else 'BUY'
        qty = int(sig.get('numContract', 1))
    
        sig2 = dict(sig)
        sig2['direction'] = exitAction
    
        # Force MKT when requested (EOD)
        if forceMkt and hasattr(self.order, 'ButterflyMktOrder'):
            orderId = self.order.ButterflyMktOrder(self.optionContracts, sig2, qty, exitAction)
        elif hasattr(self.order, 'ButterflyMktOrder'):
            orderId = self.order.ButterflyMktOrder(self.optionContracts, sig2, qty, exitAction)
        else:
            lmt = float(spreadBid if exitAction == 'SELL' else spreadAsk)
            lmt = float(max(lmt, 0.01))
            sig2['limit price'] = lmt
            orderId = self.order.ButterflyLmtOrder(self.optionContracts, sig2, qty, lmt)
    
        meta = {'strategy': 'skew butterfly',
                'signal': signalKey,
                'reason': reason,
                'entry fill': entryFillPrice.get(signalKey),
                'qty': qty}
        if isinstance(extra, dict):
            meta.update(extra)
    
        self.ordManager.Register(orderId, meta=meta)
        exitOrderId[signalKey] = orderId
        
    def ButterflyModelQuote(self, signalDict, optionPrices):
        if optionPrices is None:
            return None
        
        legs = []
        def AddLeg(optType, strike, sign):
            if strike is None:
                return
            
            try:
                k = str(int(float(strike)))
            except Exception:
                k = str(strike)
            legs.append((optType, k, sign))
        
        AddLeg('put',  signalDict.get('long put 1') , +1)
        AddLeg('put',  signalDict.get('long put 2') , +1)
        AddLeg('put',  signalDict.get('short put 1'), -1)
        AddLeg('put',  signalDict.get('short put 2'), -1)

        AddLeg('call', signalDict.get('long call 1') , +1)
        AddLeg('call', signalDict.get('long call 2') , +1)
        AddLeg('call', signalDict.get('short call 1'), -1)
        AddLeg('call', signalDict.get('short call 2'), -1)
        
        if not legs:
            return None

        spreadBid = 0.0
        spreadAsk = 0.0

        for optType, k, sign in legs:
            try:
                row = optionPrices.loc[(optType, k)]
            except Exception:
                return None

            bid = float(row.get('model bid', 0.0))
            ask = float(row.get('model ask', 0.0))
            if bid <= 0.0 and ask <= 0.0:
                return None

            if sign > 0:
                spreadBid += bid
                spreadAsk += ask
            else:
                spreadBid -= ask
                spreadAsk -= bid

        spreadMid = (spreadBid + spreadAsk) / 2.0
        return spreadBid, spreadAsk, spreadMid
    
    def CancelAllEntryOrders(self, activeEntryOrder, batchStart = None, lastSignal = None, entryWinner = None, 
                             signalKeys = None):
        '''
        Cancel all outstanding ENTRY orders across signals
        Clears activeEntryOrder lists and resets batchStart/lastSignal if provided
        '''
        
        keys = signalKeys or list(activeEntryOrder.keys())
        
        for sk in keys:
            ids = list(activeEntryOrder.get(sk, []))
            for orderId in ids:
                if self.ordManager.Working(orderId):
                    self.ordManager.Cancel(orderId)
                    
            activeEntryOrder[sk] = []
            
            if batchStart is not None:
                batchStart[sk] = None
            if lastSignal is not None:
                lastSignal[sk] = None
            if entryWinner is not None:
                entryWinner[sk] = None
                
    def ManageEODLiquidation(self, signalKey, inTrade, tradeSignalDict, exitOrderId, exitInProgress, entryFillPrice):
        if not inTrade.get(signalKey, False):
            return
        if exitInProgress.get(signalKey, False):
            return
    
        sig = tradeSignalDict.get(signalKey)
        if not isinstance(sig, dict) or not sig:
            return
    
        direction = str(sig.get('direction', '')).upper()
        if direction not in ('BUY', 'SELL'):
            return
    
        # For forced EOD liquidation, do not depend on live quotes
        # if a market combo order method exists.
        if hasattr(self.order, 'ButterflyMktOrder'):
            return self.PlaceExit(signalKey, sig, direction, 0.01, 0.01,
                                  entryFillPrice = entryFillPrice,
                                  exitOrderId    = exitOrderId,
                                  exitInProgress = exitInProgress,
                                  reason         = 'EOD liquidation',
                                  extra          = {'type': 'EOD'},
                                  forceMkt       = True)
    
        # Fallback only if market combo order is unavailable
        q = self.ButterflyQuote(sig)
        if q is None:
            return
    
        spreadBid, spreadAsk, _ = q
        return self.PlaceExit(signalKey, sig, direction, spreadBid, spreadAsk,
                              entryFillPrice = entryFillPrice,
                              exitOrderId    = exitOrderId,
                              exitInProgress = exitInProgress,
                              reason         = 'EOD liquidation',
                              extra          = {'type': 'EOD'},
                              forceMkt       = True)
    
    def ButterflyLegQuotes(self, signalDict):
        out = {}
    
        def AddLeg(label, optType, strike):
            if strike is None:
                return
            try:
                k_num = int(float(strike))
                k = str(k_num)
            except Exception:
                k_num = strike
                k = str(strike)
    
            sym = f'{optType}_{k}'
            out[f'{label} strike'] = k_num
            out[f'{label} bid'] = float(self.tws.mktDataBid.get(sym, 0.0))
            out[f'{label} ask'] = float(self.tws.mktDataAsk.get(sym, 0.0))
    
        AddLeg('long call 1',  'call', signalDict.get('long call 1'))
        AddLeg('short call 1', 'call', signalDict.get('short call 1'))
        AddLeg('long call 2',  'call', signalDict.get('long call 2'))
        AddLeg('short call 2', 'call', signalDict.get('short call 2'))
    
        AddLeg('long put 1',   'put',  signalDict.get('long put 1'))
        AddLeg('short put 1',  'put',  signalDict.get('short put 1'))
        AddLeg('long put 2',   'put',  signalDict.get('long put 2'))
        AddLeg('short put 2',  'put',  signalDict.get('short put 2'))
    
        return out
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            