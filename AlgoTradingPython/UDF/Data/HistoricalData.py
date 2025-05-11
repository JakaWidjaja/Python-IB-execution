
class HistoricalData:
    def __init__(self):
        pass
    
    def GetHistoricalData(self, tws, reqId, contract, durationStr, barSizeSetting, endDateTime = '', 
                          whatToShow = 'MIDPOINT', useRTH = 1, formatDate = 1, keepUpToDate = False,  \
                          chartOptions = []):
        self.tws            = tws
        self.reqId          = reqId
        self.contract       = contract
        self.durationStr    = durationStr
        self.barSizeSetting = barSizeSetting
        self.endDateTime    = endDateTime
        self.whatToShow     = whatToShow
        self.useRTH         = useRTH
        self.formatDate     = formatDate
        self.keepUpToDate   = keepUpToDate
        self.chartOptions   = chartOptions
        
        tws.reqHistoricalData(reqId          = self.reqId, 
                              contract       = self.contract, 
                              endDateTime    = self.endDateTime, 
                              durationStr    = self.durationStr, 
                              barSizeSetting = self.barSizeSetting, 
                              whatToShow     = self.whatToShow, 
                              useRTH         = self.useRTH, 
                              formatDate     = self.formatDate, 
                              keepUpToDate   = self.keepUpToDate, 
                              chartOptions   = self.chartOptions)
        