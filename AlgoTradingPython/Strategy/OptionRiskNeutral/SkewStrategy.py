import sys
sys.path.append("/home/lun/Desktop/Folder 2/AlgoTradingPython/Strategy/OptionPricing")

import Black76
import numpy as np

class SkewStrategy:
    def __init__(self, riskReversalThresholdUpper, riskReversalThresholdLower, 
                 butterflyPutThresholdUpper , butterflyPutThresholdLower,
                 butterflyCallThresholdUpper, butterflyCallThresholdLower, 
                 expiry, intRate):
        
        self.riskReversalThresholdUpper  = riskReversalThresholdUpper
        self.riskReversalThresholdLower  = riskReversalThresholdLower
        self.butterflyPutThresholdUpper  = butterflyPutThresholdUpper
        self.butterflyPutThresholdLower  = butterflyPutThresholdLower
        self.butterflyCallThresholdUpper = butterflyCallThresholdUpper
        self.butterflyCallThresholdLower = butterflyCallThresholdLower
        self.expiry  = expiry
        self.intRate = intRate
        
        self.bl76 = Black76.Black76()
    
    def EntrySignal(self, mktIVCall, mktCallBid, mktCallAsk, mktPutBid, mktPutAsk, 
                                     mdlCallBid, mdlCallAsk, mdlPutBid, mdlPutAsk, undPrice, strikes):
        atmStrike = min(strikes, key = lambda x : abs(undPrice - x))
        atmIndex = strikes.index(atmStrike)
        
        # ATM Vega
        atmVol = mktIVCall[atmIndex]
        atmVega = self.bl76.Vega(undPrice, atmStrike, atmVol, self.expiry, self.intRate)

        # Risk Reversal
        riskReversal = self.RiskReversal(mktCallBid, mktCallAsk, mktPutBid, mktPutAsk, 
                                         mdlCallBid, mdlCallAsk, mdlPutBid, mdlPutAsk, 
                                         atmIndex, strikes, atmVega)
        
        # Butterfly
        butterfly = self.Butterfly(mktCallBid, mktCallAsk, mktPutBid, mktPutAsk, 
                                   mdlCallBid, mdlCallAsk, mdlPutBid, mdlPutAsk, atmIndex, strikes)
        
        res = {'risk reversal'    : riskReversal, 
               'butterfly'        : butterfly}
        
        return res
        
    def RiskReversal(self, mktCallBid, mktCallAsk, mktPutBid, mktPutAsk, 
                           mdlCallBid, mdlCallAsk, mdlPutBid, mdlPutAsk, atmIndex, strikes, atmVega):
        mktCallMid = list((np.asarray(mktCallBid) + np.asarray(mktCallAsk)) / 2.0)
        mktPutMid  = list((np.asarray(mktPutBid)  + np.asarray(mktPutAsk))  / 2.0)
        mdlCallMid = list((np.asarray(mdlCallBid) + np.asarray(mdlCallAsk)) / 2.0)
        mdlPutMid  = list((np.asarray(mdlPutBid)  + np.asarray(mdlPutAsk))  / 2.0)
        
        rrMarket_1 = (mktPutMid[atmIndex - 1] - mktCallMid[atmIndex + 1]) / atmVega
        rrMarket_2 = (mktPutMid[atmIndex - 2] - mktCallMid[atmIndex + 2]) / atmVega

        rrModel_1 = (mdlPutMid[atmIndex - 1] - mdlCallMid[atmIndex + 1]) / atmVega
        rrModel_2 = (mdlPutMid[atmIndex - 2] - mdlCallMid[atmIndex + 2]) / atmVega
        
        rr_1 = abs(rrMarket_1 - rrModel_1)
        rr_2 = abs(rrMarket_2 - rrModel_2)
        #print('rr 1', rr_1, rrMarket_1, rrModel_1)
        #print('rr 2', rr_2, rrMarket_2, rrModel_2)
        
        # Long
        longDirection = False
        if abs(rr_1) >= abs(rr_2):
            if rr_1 < self.riskReversalThresholdLower:
                longDirection  = True
                longPutStrike  = strikes[atmIndex - 1]
                longCallStrike = strikes[atmIndex + 1]
        elif abs(rr_2) > abs(rr_1):
            if rr_2 < self.riskReversalThresholdLower:
                longDirection  = True
                longPutStrike  = strikes[atmIndex - 2]
                longCallStrike = strikes[atmIndex + 2]

        if longDirection:
            long = {'short Put' : longPutStrike, 'long call' : longCallStrike,
                    'market 1' : rrMarket_1, 'market 2' : rrMarket_2, 
                    'model 1' : rrModel_1, 'model 2' : rrModel_2}
        else:
            long = 0.0
            
        # Short
        shortDirection = False
        if abs(rr_1) >= abs(rr_2):
            if rr_1 > self.riskReversalThresholdUpper:
                shortDirection  = True
                shortPutStrike  = strikes[atmIndex - 1]
                shortCallStrike = strikes[atmIndex + 1]
        elif abs(rr_2) > abs(rr_1):
            if rr_2 > self.riskReversalThresholdUpper:
                shortDirection  = True
                shortPutStrike  = strikes[atmIndex - 2]
                shortCallStrike = strikes[atmIndex + 2]
        
        if shortDirection:
            short = {'long Put' : shortPutStrike, 'short call' : shortCallStrike,
                    'market 1' : rrMarket_1, 'market 2' : rrMarket_2, 
                    'model 1' : rrModel_1, 'model 2' : rrModel_2}
        else:
            short = 0.0
        
        return [long, short]
    
    def Butterfly(self, mktCallBid, mktCallAsk, mktPutBid, mktPutAsk, 
                           mdlCallBid, mdlCallAsk, mdlPutBid, mdlPutAsk, atmIndex, strikes):
        # These are 3 strikes on the put-wing side of ATM in your original logic:
        # K1 = atmIndex-3, K2 = atmIndex-2 (middle), K3 = atmIndex-1
        i1, i2, i3 = atmIndex - 3, atmIndex - 2, atmIndex - 1
        c1, c2, c3 = atmIndex + 1, atmIndex + 2, atmIndex + 3
    
        # Put BUY-side executable price
        mktPutBuy  = mktPutAsk[i1] - 2.0 * mktPutBid[i2] + mktPutAsk[i3]
        mdlPutBuy  = mdlPutAsk[i1] - 2.0 * mdlPutBid[i2] + mdlPutAsk[i3]
        
        # Put SELL-side executable price
        mktPutSell = mktPutBid[i1] - 2.0 * mktPutAsk[i2] + mktPutBid[i3]
        mdlPutSell = mdlPutBid[i1] - 2.0 * mdlPutAsk[i2] + mdlPutBid[i3]
        
        # Call BUY-side executable price
        mktCallBuy  = mktCallAsk[c1] - 2.0 * mktCallBid[c2] + mktCallAsk[c3]
        mdlCallBuy  = mdlCallAsk[c1] - 2.0 * mdlCallBid[c2] + mdlCallAsk[c3]
        
        # Call SELL-side executable price
        mktCallSell = mktCallBid[c1] - 2.0 * mktCallAsk[c2] + mktCallBid[c3]
        mdlCallSell = mdlCallBid[c1] - 2.0 * mdlCallAsk[c2] + mdlCallBid[c3]
        
        # Diff
        diffPutBuy   = mktPutBuy  - mdlPutBuy
        diffPutSell  = mktPutSell - mdlPutSell
        diffCallBuy  = mktCallBuy  - mdlCallBuy
        diffCallSell = mktCallSell - mdlCallSell

        p1 = strikes[i1]
        p2 = strikes[i2]  # middle strike (x2)
        p3 = strikes[i3]
        
        call1 = strikes[c1]
        call2 = strikes[c2]
        call3 = strikes[c3]

        #========================================================================================
        #========================================================================================
        # Put
        # diff < 0 => market butterfly cheaper than model -> BUY butterfly (long convexity)
        #print('Buy: ', diffPutBuy, self.butterflyPutThresholdLower)
        if diffPutBuy < self.butterflyPutThresholdLower:
            butterflyPutBuy =  {'long put 1'  : p1,
                                'long put 2'  : p3,
                                'short put 1' : p2,
                                'short put 2' : p2, 
                                'direction'   : 'BUY',
                                'limit price' : mktPutBuy}
        else:
            butterflyPutBuy = 0.0

        # diff > 0 => market butterfly richer than model -> SELL butterfly (short convexity)
        #print('Sell: ', diffPutSell, self.butterflyPutThresholdUpper)
        if diffPutSell > self.butterflyPutThresholdUpper:
            butterflyPutSell = {'short put 1' : p1,
                                'short put 2' : p3,
                                'long put 1'  : p2,
                                'long put 2'  : p2, 
                                'direction'   : 'SELL', 
                                'limit price' : mktPutSell}
        else:
            butterflyPutSell = 0.0
        #========================================================================================
        #========================================================================================
        
        #========================================================================================
        #========================================================================================
        # Call
        # diff < 0 => market butterfly cheaper than model -> BUY butterfly (long convexity)
        if diffCallBuy < self.butterflyCallThresholdLower:
            butterflyCallBuy =  {'long call 1'  : call1,
                                 'long call 2'  : call3,
                                 'short call 1' : call2,
                                 'short call 2' : call2, 
                                 'direction'    : 'BUY',
                                 'limit price'  : mktCallBuy}
        else:
            butterflyCallBuy = 0.0
        # diff > 0 => market butterfly richer than model -> SELL butterfly (short convexity)
        if diffCallSell > self.butterflyCallThresholdUpper:
            butterflyCallSell = {'short call 1' : call1,
                                 'short call 2' : call3,
                                 'long call 1'  : call2,
                                 'long call 2'  : call2,
                                 'direction'    : 'SELL', 
                                 'limit price'  : mktCallSell}
        else:
            butterflyCallSell = 0.0
        #========================================================================================
        #========================================================================================
        return [butterflyCallBuy, butterflyCallSell, butterflyPutBuy, butterflyPutSell]
