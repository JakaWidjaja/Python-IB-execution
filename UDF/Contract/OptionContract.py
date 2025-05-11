class OptionContract():
    def __init__(self):
        pass
    
    def contract(self, twsContract, symbol, secType, currency, exchange, optType, strike, lastTradeDateOrContractMonth, 
                 multiplier):
        self.twsContract = twsContract
        self.symbol      = symbol
        self.secType     = secType
        self.currency    = currency
        self.exchange    = exchange
        self.optType     = optType
        self.strike      = strike
        self.lastTradeDateOrContractMonth = lastTradeDateOrContractMonth
        self.multiplier  = multiplier
        
        self.twsContract.symbol     = self.symbol
        self.twsContract.secType    = self.secType
        self.twsContract.currency   = self.currency
        self.twsContract.exchange   = self.exchange
        self.twsContract.right      = self.optType
        self.twsContract.strike     = self.strike
        self.twsContract.multiplier = self.multiplier
        self.twsContract.lastTradeDateOrContractMonth = self.lastTradeDateOrContractMonth
        
        return self.twsContract