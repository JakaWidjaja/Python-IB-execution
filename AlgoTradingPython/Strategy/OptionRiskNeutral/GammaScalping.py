import sys
sys.path.append("/home/lun/Desktop/Folder 2/AlgoTradingPython/Strategy/OptionPricing")

import Black76

class GammaScalping:
    def __init__(self, straddleTriggerLevel, convexTriggerLevel, skewTriggerLevelUpper, skewTriggerLevelLower, 
                 expiry, rate):
        self.straddleTriggerLevel  = straddleTriggerLevel
        self.convexTriggerLevel    = convexTriggerLevel
        self.skewTriggerLevelUpper = skewTriggerLevelUpper
        self.skewTriggerLevelLower = skewTriggerLevelLower
        self.expiry                = expiry
        self.rate                  = rate
        
        self.bl76 = Black76.Black76()
    
    def EntrySignal(self, mktCallBid, mktCallAsk, mktPutBid, mktPutAsk, 
                          mdlCallBid, mdlCallAsk, mdlPutBid, mdlPutAsk, mktIVCall, undPrice, strikes):
        atmStrike = min(strikes, key = lambda x : abs(undPrice - x))
        atmIndex = strikes.index(atmStrike)
        
        atmVol = mktIVCall[atmIndex]
        
        atmVega = self.bl76.Vega(undPrice, atmStrike, atmVol, self.expiry, self.rate)
        
        # Triggers        
        atmStraddle = self.ATMStraddle(mktCallBid[atmIndex], mktCallAsk[atmIndex], mktPutBid[atmIndex], mktPutAsk[atmIndex], 
                                       mdlCallBid[atmIndex], mdlCallAsk[atmIndex], mdlPutBid[atmIndex], mdlPutAsk[atmIndex])
        
        convexity   = self.Convexity(mktCallAsk[atmIndex - 1], mktCallBid[atmIndex], mktCallAsk[atmIndex + 1], 
                                     mdlCallAsk[atmIndex - 1], mdlCallBid[atmIndex], mdlCallAsk[atmIndex + 1])
        
        skewPairsATM = self.SkewPairs(mktCallBid[atmIndex], mktCallAsk[atmIndex], mktPutBid[atmIndex], mktPutAsk[atmIndex], 
                                       mdlCallBid[atmIndex], mdlCallAsk[atmIndex], mdlPutBid[atmIndex], mdlPutAsk[atmIndex],
                                       atmVega)
        
        skewPairsWide = self.SkewPairs(mktCallBid[atmIndex + 1], mktCallAsk[atmIndex + 1], 
                                       mktPutBid[atmIndex - 1], mktPutAsk[atmIndex - 1], 
                                       mdlCallBid[atmIndex + 1], mdlCallAsk[atmIndex + 1],
                                       mdlPutBid[atmIndex - 1], mdlPutAsk[atmIndex - 1], atmVega)
        
        # Decision
        if atmStraddle > self.straddleTriggerLevel:
            if convexity > self.convexTriggerLevel:
                if skewPairsATM <= self.skewTriggerLevelUpper and skewPairsATM >= self.skewTriggerLevelLower:
                    return {'long call' : atmStrike, 'long put' : atmStrike}
                elif skewPairsWide > self.skewTriggerLevelUpper:
                    return {'long call' : strikes[atmIndex + 1], 'long put' : strikes[atmIndex - 1]}
                elif skewPairsWide < self.skewTriggerLevelLower:
                    return {'long put': strikes[atmIndex - 1], 'long call' : atmStrike}
                else:
                    return 0.0
                    
            else:
                return 0.0
        else:
            return 0.0
    
    def ATMStraddle(self, mktCallBid, mktCallAsk, mktPutBid, mktPutAsk, mdlCallBid, mdlCallAsk, mdlPutBid, mdlPutAsk):
        mktCallPrice = (mktCallBid + mktCallAsk) / 2.0
        mktPutPrice  = (mktPutBid + mktPutAsk)   / 2.0
        
        modelCallPrice = (mdlCallBid + mdlCallAsk) / 2.0
        modelPutPrice  = (mdlPutBid + mdlPutAsk)   / 2.0
        
        mktStraddle   = mktCallPrice + mktPutPrice
        modelStraddle = modelCallPrice + modelPutPrice
        
        return modelStraddle - mktStraddle
        
    
    def Convexity(self, mktCallPrice_1, mktCallPrice_2, mktCallPrice_3, 
                        modelCallPrice_1, modelCallPrice_2, modelCallPrice_3):
        mktConvex   = mktCallPrice_1 - 2 * mktCallPrice_2 + mktCallPrice_3
        modelConvex = modelCallPrice_1 - 2 * modelCallPrice_2 + modelCallPrice_3
        
        return modelConvex - mktConvex
        
    def SkewPairs(self, mktCallBid, mktCallAsk, mktPutBid, mktPutAsk, mdlCallBid, mdlCallAsk, mdlPutBid, mdlPutAsk, atmVega):
        mktPutPrice  = (mktPutBid  + mktPutAsk)  / 2.0
        mktCallPrice = (mktCallBid + mktCallAsk) / 2.0
        
        modelPutPrice  = (mdlPutBid  + mdlPutAsk)  / 2.0
        modelCallPrice = (mdlCallBid + mdlCallAsk) / 2.0
        
        diffPut  = (mktPutPrice  - modelPutPrice)  / atmVega
        diffCall = (mktCallPrice - modelCallPrice) / atmVega
        
        return diffPut - diffCall
        