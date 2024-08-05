class EntryExit:
    def __init__(self):
        pass
    
    def EntryRisingPrice(self, timeSeries, triggerPrice):
        '''
        Price is increasing, so go long
        '''
        self.timeSeries   = timeSeries
        self.triggerPrice = triggerPrice
        
        if self.timeSeries[-3] < self.triggerPrice and self.timeSeries[-2] < self.triggerPrice and \
                    self.timeSeries[-1] > self.triggerPrice:
            return 'Enter Long'
        else:
            return 'Pass'
        
    def EntryFallingPrice(self, timeSeries, triggerPrice):
        '''
        Price is falling, so go short
        '''
        self.timeSeries   = timeSeries
        self.triggerPrice = triggerPrice
        
        if self.timeSeries[-3] > self.triggerPrice and self.timeSeries[-2] > self.triggerPrice and \
                    self.timeSeries[-1] < self.triggerPrice:
            return 'Enter Short'
        else:
            return 'Pass'
