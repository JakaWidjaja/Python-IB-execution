class FuturesContract:
    def __init__(self):
        pass
    
    def contract(self, twsContract, symbol, secType, currency, exchange, expiry, multiplier):
        self.twsContract = twsContract
        self.symbol      = symbol
        self.secType     = secType
        self.currency    = currency
        self.exchange    = exchange
        #self.lastTradeDateOrContractMonth = lastTradeDateOrContractMonth
        self.multiplier  = multiplier
        self.expiry = expiry
        
        self.twsContract.symbol     = self.symbol
        self.twsContract.secType    = self.secType
        self.twsContract.currency   = self.currency
        self.twsContract.exchange   = self.exchange
        self.twsContract.multiplier = self.multiplier
        #self.twsContract.lastTradeDateOrContractMonth = self.lastTradeDateOrContractMonth
        self.twsContract.expiry = self.expiry
        
        return self.twsContract