import sys
sys.path.append("/home/lun/Desktop/Folder 2/AlgoTradingPython/Strategy/OptionPricing")
sys.path.append("/home/lun/Desktop/Folder 2/AlgoTradingPython/Strategy/OptionRiskNeutral")

import numpy as np

import Black76
import GammaScalping
import SkewStrategy

class OptionArbitrage:
    def __init__(self, straddleTriggerLevel, convexTriggerLevel, skewTriggerLevelUpper, skewTriggerLevelLower, 
                       riskReversalThresholdUpper,riskReversalThresholdLower, 
                       butterflyPutThresholdUpper, butterflyPutThresholdLower, 
                       butterflyCallThresholdUpper, butterflyCallThresholdLower, 
                       expiry, intRate):
        
        self.straddleTriggerLevel  = straddleTriggerLevel
        self.convexTriggerLevel    = convexTriggerLevel
        self.skewTriggerLevelUpper = skewTriggerLevelUpper
        self.skewTriggerLevelLower = skewTriggerLevelLower
        
        self.riskReversalThresholdUpper = riskReversalThresholdUpper
        self.riskReversalThresholdLower = riskReversalThresholdLower
        
        self.butterflyPutThresholdUpper  = butterflyPutThresholdUpper
        self.butterflyPutThresholdLower  = butterflyPutThresholdLower
        self.butterflyCallThresholdUpper = butterflyCallThresholdUpper
        self.butterflyCallThresholdLower = butterflyCallThresholdLower
        
        self.expiry                = expiry
        self.intRate               = intRate
        
        self.bl76 = Black76.Black76()
        self.gamma = GammaScalping.GammaScalping(self.straddleTriggerLevel, self.convexTriggerLevel, 
                                                 self.skewTriggerLevelUpper, self.skewTriggerLevelLower,
                                                 self.expiry, self.intRate)
        self.skew = SkewStrategy.SkewStrategy(self.riskReversalThresholdUpper, self.riskReversalThresholdLower, 
                                              self.butterflyPutThresholdUpper, self.butterflyPutThresholdLower,
                                              self.butterflyCallThresholdUpper, self.butterflyCallThresholdLower,
                                              self.expiry, self.intRate)

    def ParamSetUp(self, optionData, undPrice, expiry, intRate = 0.0):
        optionData = optionData.reset_index()
        optionData = optionData.sort_values(by = ['type', 'strike'])
        
        self.strikes = list(optionData.loc[optionData['type'] == 'call', 'strike'])
        self.strikes = list(map(float, self.strikes))
        
        self.mktCallBid = list(optionData.loc[optionData['type'] == 'call', 'mkt bid'])
        self.mktCallAsk = list(optionData.loc[optionData['type'] == 'call', 'mkt ask'])
        self.mktPutBid  = list(optionData.loc[optionData['type'] == 'put' , 'mkt bid'])
        self.mktPutAsk  = list(optionData.loc[optionData['type'] == 'put' , 'mkt ask'])

        self.mdlCallBid = list(optionData.loc[optionData['type'] == 'call', 'model bid'])
        self.mdlCallAsk = list(optionData.loc[optionData['type'] == 'call', 'model ask'])
        self.mdlPutBid  = list(optionData.loc[optionData['type'] == 'put' , 'model bid'])
        self.mdlPutAsk  = list(optionData.loc[optionData['type'] == 'put' , 'model ask'])
        
        self.undPrice = undPrice
        self.expiry   = expiry
        self.intRate  = intRate
        
    def ImpliedVol(self, dataType):
        if dataType == 'market':
            callMid = (np.asarray(self.mktCallBid) + np.asarray(self.mktCallAsk)) / 2.0
            putMid  = (np.asarray(self.mktPutBid)  + np.asarray(self.mktPutAsk)) / 2.0
            optionCall = callMid.tolist()
            optionPut  = putMid.tolist()
        elif dataType == 'gg':
            callMid = (np.asarray(self.mdlCallBid) + np.asarray(self.mdlCallAsk)) / 2.0
            putMid  = (np.asarray(self.mdlPutBid)  + np.asarray(self.mdlPutAsk)) / 2.0 
            optionCall = callMid.tolist()
            optionPut  = putMid.tolist()
        
        atmStrike = min(self.strikes, key = lambda x : (abs(x - self.undPrice)))
        atmIndex = self.strikes.index(atmStrike)
        
        # Put and call IV are the same. Use put IV for ATM. 
        # Strikes
        useStrike = self.strikes[ : atmIndex + 1] + self.strikes[atmIndex + 1 : ]

        # Option prices
        putPrice = optionPut[ : atmIndex + 1]
        callPrice = optionCall[atmIndex + 1 : ]
        optionPrice = putPrice + callPrice

        # Option type (call or put)
        optionType = ['put'] * (atmIndex + 1) + ['call'] * (len(self.strikes) - (atmIndex + 1))

        impVol = [self.bl76.ImpliedVol(optPrice, self.undPrice, k, self.expiry, self.intRate, optType) 
                  for optPrice, k, optType in zip(optionPrice, useStrike, optionType)]

        return impVol
        
        
    def Arbitrage(self):
        mktIVCall = self.ImpliedVol('market')       

        skew = self.skew.EntrySignal(mktIVCall,self.mktCallBid, self.mktCallAsk, self.mktPutBid, self.mktPutAsk,
                                     self.mdlCallBid, self.mdlCallAsk, self.mdlPutBid, self.mdlPutAsk,
                                     self.undPrice, self.strikes)
        
        gammaScalp = self.gamma.EntrySignal(self.mktCallBid, self.mktCallAsk, self.mktPutBid, self.mktPutAsk,
                                            self.mdlCallBid, self.mdlCallAsk, self.mdlPutBid, self.mdlPutAsk,
                                            mktIVCall, self.undPrice, self.strikes)
        
        output = {'skew' : skew, 'gamma' : gammaScalp}
        
        return output
        
        

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        