class Interpolation:
    def __init__(self):
        pass
    
    def Linear(self, price1, price2, time1, time2, targetTime):
        '''
        price1 < price2
        time1 < targetTime < time2
        '''
        
        targetPrice = price1 + ((targetTime - time1) / (time2 - time1)) * (price2 - price1)
        
        return targetPrice