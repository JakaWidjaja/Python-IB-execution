class OptionContract():
    def __init__(self):
        pass
    
    def contract(self, twsContract, symbol, secType, currency, exchange, optType, strike, lastTradeDateOrContractMonth, 
                 tradingClass, multiplier):
        
        twsContract.symbol                       = symbol
        twsContract.secType                      = secType
        twsContract.currency                     = currency
        twsContract.exchange                     = exchange
        twsContract.right                        = optType
        twsContract.strike                       = str(int(strike))
        twsContract.multiplier                   = str(int(multiplier))
        twsContract.lastTradeDateOrContractMonth = str(int(lastTradeDateOrContractMonth))
        twsContract.tradingClass                 = tradingClass
        
        return twsContract