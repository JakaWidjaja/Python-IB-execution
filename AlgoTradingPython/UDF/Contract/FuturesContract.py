import pandas as pd
import math

class FuturesContract:
    def __init__(self):
        pass
    
    def contract(self, twsContract, secType, currency, exchange, symbol = None, lastTradeDateOrContractMonth = None,
                 multiplier = None, tradingClass = None, localSymbol = None):
        
        twsContract.secType  = secType
        twsContract.currency = currency
        twsContract.exchange = exchange
        
        symbol = self.CleanField(symbol)
        if symbol is not None:
            twsContract.symbol = symbol
        
        multiplier = self.CleanField(multiplier)
        if multiplier is not None:
            twsContract.multiplier = str(multiplier)
            
        lastTradeDateOrContractMonth = self.Clean_ym_or_ymd(lastTradeDateOrContractMonth)
        if lastTradeDateOrContractMonth is not None:
            twsContract.lastTradeDateOrContractMonth = str(int(lastTradeDateOrContractMonth))
            
        tradingClass = self.CleanField(tradingClass)
        if tradingClass is not None:
            twsContract.tradingClass = tradingClass
            
        localSymbol = self.CleanField(localSymbol)
        if localSymbol is not None:
            twsContract.localSymbol = localSymbol
        
        return twsContract
    
    def CleanField(self, x):
        # Convert NaN / None to None
        if x is None:
            return None
        # pandas NaN
        try:
            if pd.isna(x):
                return None
        except Exception:
            pass
        return x

    def Clean_ym_or_ymd(self, x):
        x = self.CleanField(x)
        if x is None:
            return None

        # Excel often gives floats like 20260317.0
        if isinstance(x, float):
            if math.isnan(x):
                return None
            x = int(x)

        # If it's already int, keep it
        if isinstance(x, int):
            return str(x)

        # If it's a string like "20260317" or "202603"
        s = str(x).strip()
        # Remove a trailing ".0" if present
        if s.endswith(".0"):
            s = s[:-2]
        return s