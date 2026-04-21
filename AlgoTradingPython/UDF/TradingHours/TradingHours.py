import datetime as dt
from zoneinfo import ZoneInfo 
import threading
import re

class TradingHours:
    def __init__(self, tws, localTimeZone="Australia/Sydney"):
        self.tws = tws
        self.localTimeZone = ZoneInfo(localTimeZone)
        
    def GetTradingHours(self, contract, timeout = 3.0):
        reqId = self.tws.getNextReqId()
        
        self.tws.contractDetailsEndEvent[reqId] = threading.Event()
        with self.tws.contractDetailsLock:
            self.tws.contractDetailsData[reqId] = []
    
        # Request
        self.tws.reqContractDetails(reqId, contract)
    
        # Wait for contractDetailsEnd
        if not self.tws.contractDetailsEndEvent[reqId].wait(timeout):
            raise TimeoutError("No contract details received (contractDetailsEnd timeout)")
    
        # Read response
        with self.tws.contractDetailsLock:
            rows = self.tws.contractDetailsData.get(reqId, [])
    
        if not rows:
            raise RuntimeError("contractDetails returned no rows")
    
        cd = rows[0]
        return cd.tradingHours, cd.liquidHours, cd.timeZoneId
    
    def ParseIBHours(self, hoursStr, today):
        ymd = today.strftime('%Y%m%d')

        for block in hoursStr.split(';'):
            block = block.strip()
            if not block:
                continue
    
            if not block.startswith(ymd + ":"):
                continue
    
            if "CLOSED" in block:
                return None
    
            m = re.match(r"^(\d{8}):(\d{4})-(\d{8}):(\d{4})$", block)
            if not m:
                continue
    
            return m.groups()  # (start_date, start_hhmm, end_date, end_hhmm)
    
        return None
    
    def HHMMToTime(self, hhmm):
        return dt.time(int(hhmm[:2]), int(hhmm[2:]))
    
    def GetLocalOpenClosedDT(self, contract, today = None, useLiquid = True, timeout = 3.0):
        tradingHours, liquidHours, timeZoneName = self.GetTradingHours(contract, timeout=timeout)
        exchangeTZ = ZoneInfo(timeZoneName)
    
        if today is None:
            today = dt.datetime.now(exchangeTZ).date()
    
        hoursStr = liquidHours if useLiquid else tradingHours
        parsed = self.ParseIBHours(hoursStr, today)
        if parsed is None:
            return None, None, timeZoneName
    
        start_date, openHHMM, end_date, closeHHMM = parsed
    
        open_date_ex  = dt.datetime.strptime(start_date, "%Y%m%d").date()
        close_date_ex = dt.datetime.strptime(end_date, "%Y%m%d").date()
    
        openDT_ex  = dt.datetime.combine(open_date_ex,  self.HHMMToTime(openHHMM),  tzinfo=exchangeTZ)
        closeDT_ex = dt.datetime.combine(close_date_ex, self.HHMMToTime(closeHHMM), tzinfo=exchangeTZ)
    
        openDT_local  = openDT_ex.astimezone(self.localTimeZone)
        closeDT_local = closeDT_ex.astimezone(self.localTimeZone)
    
        return openDT_local, closeDT_local, timeZoneName