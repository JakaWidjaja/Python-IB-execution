import time

class Positions:
    def __init__(self, tws):
        self.tws = tws
    
    def GetPortPosition(self, timeDelay):
        self.timeDelay = timeDelay
        
        self.tws.reqPositions()

        time.sleep(self.timeDelay)
        
        return self.tws.dfPosition