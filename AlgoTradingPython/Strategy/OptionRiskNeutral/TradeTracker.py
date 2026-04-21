import pandas as pd
import datetime as dt
import os

class TradeTracker:
    def __init__(self, outLocation, prefix = 'ledger'):
        self.outLocation = outLocation
        self.prefix      = prefix
        
        os.makedirs(self.outLocation, exist_ok=True)
        
        self.rows = []
        self.active = {}
        self.realisedPnl = {}
        self.realisedCumPnl = 0.0
        
        # For collecting bid/ask prices
        self.surfCols = None
        self.surfKeyToOffset = {}
        self.surfRows = []
        
    def MakeTradeId(self, signalKey, entryOrderId):
        ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        return f'{signalKey}_{ts}_{entryOrderId}'
    
    @staticmethod
    def CalcPnl(direction, entry, mark):
        '''
        BUY : pnl = mark - entry
        SELL: pnl = entry - mark
        '''
        
        if entry is None or mark is None:
            return None
        if entry <= 0:
            return None
        
        direction = (direction or '').upper()
        if direction == 'BUY':
            return mark - entry
        elif direction == 'SELL':
            return entry - mark
        return None
    
    def Append(self, row):
        if 'ts' not in row:
            row['ts'] = dt.datetime.now()
        self.rows.append(row)
        
    def OnEntryFilled(self, signalKey, entryOrderId, direction, qty, entryFill, futuresPrice = None, mktBid = None,
                      mktAsk = None, mktMid = None, modelBid = None, modelAsk = None, modelMid = None, diff = None, 
                      legQuotes = None):
        tradeId = self.MakeTradeId(signalKey, entryOrderId)
        
        self.active[signalKey] = {'trade id'       : tradeId, 
                                  'direction'      : (direction or '').upper(), 
                                  'qty'            : int(qty), 
                                  'entry fill'     : float(entryFill)if entryFill is not None else None, 
                                  'entry order id' : entryOrderId, 
                                  'entry time'     : dt.datetime.now()}
        
        self.Append({'event'           : 'ENTRY', 
                    'signalKey'        : signalKey, 
                    'trade id'         : tradeId, 
                    'entry id'         : entryOrderId, 
                    'exit id'          : None, 
                    'exit reason'      : None, 
                    'direction'        : (direction or '').upper(), 
                    'qty'              : int(qty),
                    'futures price'    : futuresPrice, 
                    'mkt bid'          : mktBid, 
                    'mkt ask'          : mktAsk, 
                    'mkt mid'          : mktMid, 
                    'model bid'        : modelBid, 
                    'model ask'        : modelAsk, 
                    'model mid'        : modelMid, 
                    'diff'             : diff, 
                    'entry fill'       : entryFill, 
                    'exit fill'        : None, 
                    'unrealised pnl'   : 0.0, 
                    'realised pnl'     : None, 
                    'cum realised pnl' : self.realisedCumPnl, 
                    **(legQuotes or {})})
        
        return tradeId
    
    def OnMarket(self, signalKey, futuresPrice = None, mktBid = None, mktAsk = None, mktMid = None, modelBid = None, 
                 modelAsk = None, modelMid = None, diff = None):
        st = self.active.get(signalKey)
        tradeId = st['trade id'] if st else None
        
        unreal = None
        realised = None
        if st and mktMid is not None:
            unreal = self.CalcPnl(st['direction'], st['entry fill'], float(mktMid))
            if unreal is not None:
                unreal *= st['qty']
            realised = self.realisedPnl.get(tradeId)
            
        self.Append({'event' : 'Market', 
                     'signalKey' : signalKey, 
                     'trade id' : tradeId, 
                     'entry id' : st['entry order id'] if st else None, 
                     'exit id' : None, 
                     'exit reason' : None, 
                     'direction' : st['direction'] if st else None, 
                     'qty' : st['qty'] if st else None, 
                     'futures price' : futuresPrice, 
                     'mkt bid' : mktBid, 
                     'mkt ask' : mktAsk, 
                     'mkt mid' : mktMid, 
                     'model bid' : modelBid, 
                     'model ask' : modelAsk, 
                     'model mid' : modelMid, 
                     'diff' : diff, 
                     'entry fill' : st['entry fill'] if st else None, 
                     'exit fill' : None, 
                     'unrealised pnl' : unreal, 
                     'realised pnl' : realised, 
                     'cum realised pnl' : self.realisedCumPnl})
    
    def OnExitFilled(self, signalKey, exitOrderId, exitReason, exitFill, futuresPrice = None, mktBid = None, 
                     mktAsk = None, mktMid = None, modelBid = None, modelAsk = None, modelMid = None, diff = None, 
                     legQuotes = None):
        st = self.active.get(signalKey)
        if not st: # No trade
            return None
        
        tradeId   = st['trade id']
        entry     = st['entry fill']
        direction = st['direction']
        qty       = st['qty']
        
        realised = self.CalcPnl(direction, float(entry), float(exitFill))
        if realised is not None:
            realisedTotal = realised * qty
        else:
            realisedTotal = None
            
        if realisedTotal is not None:
            self.realisedPnl[tradeId] = realisedTotal
            self.realisedCumPnl       += realisedTotal
            
        self.Append({'event' : 'EXIT', 
                     'signalKey' : signalKey, 
                     'trade id' : tradeId, 
                     'entry id' : st['entry order id'], 
                     'exit id' : exitOrderId, 
                     'exit reason' : exitReason, 
                     'direction' : direction, 
                     'qty' : qty, 
                     'futures price' : futuresPrice, 
                     'mkt bid' : mktBid, 
                     'mkt ask' : mktAsk, 
                     'mkt mid' : mktMid, 
                     'model bid' : modelBid, 
                     'model ask' : modelAsk, 
                     'model mid' : modelMid, 
                     'diff' : diff, 
                     'entry fill' : entry, 
                     'exit fill' : exitFill, 
                     'unrealised pnl' : 0.0, 
                     'realised pnl' : realisedTotal, 
                     'cum realised pnl' : self.realisedCumPnl, 
                     **(legQuotes or {})})
        
        # Clear active trade
        self.active.pop(signalKey, None)
        return tradeId
    
    def ToDataframe(self):
        return pd.DataFrame(self.rows)
    
    def Flush(self, suffix = None, toExcel = False):
        df = self.ToDataframe()
        
        ts = dt.datetime.now().strftime("%Y%m%d")
        if suffix is None:
            suffix = ts

        if toExcel:
            xlsxPath = os.path.join(self.outLocation, f'{self.prefix}_{suffix}.xlsx')
            df.to_excel(xlsxPath, index = False)
        else:
            csvPath = os.path.join(self.outLocation, f'{self.prefix}_{suffix}.csv')
            df.to_csv(csvPath, index = False)
            
    # To collect the bid/ask prices
    def InitMarketSurface(self, optionContracts):
        keys = sorted(optionContracts.keys())
        
        cols = ['ts', 'futures price']
        keyToOffset = {}
        
        j = 2
        for k in keys:
            cols.extend([f'{k}_mkt_bid', 
                         f'{k}_mkt_ask', 
                         f'{k}_model_bid', 
                         f'{k}_model_ask'])
            keyToOffset[k] = j
            j += 4
        
        self.surfCols        = cols
        self.surfKeyToOffset = keyToOffset
        self.surfRows        = []
        
    def SurfaceNewRow(self, futuresPrice):
        if self.surfCols is None:
            raise RuntimeError('InitMarketSurface() must be called first')
            
        row = [None] * len(self.surfCols)
        row[0] = dt.datetime.now()
        row[1] = futuresPrice
        return row
    
    def SurfaceSet(self, row, k, mktBid, mktAsk, modelBid, modelAsk):
        off = self.surfKeyToOffset.get(k)
        if off is None:
            return
        
        row[off]     = mktBid
        row[off + 1] = mktAsk
        row[off + 2] = modelBid
        row[off + 3] = modelAsk
        
    def SurfaceAppendRow(self, row):
        self.surfRows.append(row)
        
    def FlushMarketSurface(self, suffix = None, toExcel = False):
        if not self.surfRows:
            return
        
        df = pd.DataFrame(self.surfRows, columns = self.surfCols)
        
        ts = dt.datetime.now().strftime('%Y%m%d')
        if suffix is None:
            suffix = ts
            
        if toExcel:
            path = os.path.join(self.outLocation, f'{self.prefix}_surface_{suffix}.xlsx')
            df.to_excel(path, index = False)
        else:
            path = os.path.join(self.outLocation, f'{self.prefix}_surface_{suffix}.csv')
            df.to_csv(path, index = False)
            
        
        











































