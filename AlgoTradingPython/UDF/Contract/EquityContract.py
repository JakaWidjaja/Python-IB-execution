class EquityContract():
    def __init__(self):
        pass
    
    def contract(self, twsContract, symbol, secType, currency, exchange):
        self.twsContract = twsContract
        self.symbol   = symbol
        self.secType  = secType
        self.currency = currency
        self.exchange = exchange

        self.twsContract.symbol = self.symbol
        self.twsContract.secType = self.secType
        self.twsContract.currency = self.currency
        self.twsContract.exchange = self.exchange
        
        return self.twsContract