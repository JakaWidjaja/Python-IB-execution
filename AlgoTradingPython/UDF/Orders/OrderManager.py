import time
from dataclasses import dataclass, field

workingStatus = {"PreSubmitted", "Submitted"}
doneStatus = {"Filled", "Cancelled", "ApiCancelled", "Inactive"}

@dataclass
class ManagedOrder:
    orderId      : int
    meta         : dict
    status       : str = 'PendingSubmit'
    filled       : float = 0.0
    remaining    : float = 0.0
    avgFillPrice : float = 0.0
    lastUpdate   : float = field(default_factory = time.time)
    createTime   : float = field(default_factory = time.time)

class OrderManager:
    def __init__(self, tws):
        self.tws    = tws
        self.orders = {}
        
    def Register(self, orderId, meta):
        self.orders[orderId] = ManagedOrder(orderId, meta)
        
    def OrderStatus(self, orderId, status, filled, remaining, avgFillPrice):
        o = self.orders.get(orderId)
        if o is None:
            o = ManagedOrder(orderId, meta = {'source' : 'unknown'})
            self.orders[orderId] = o
            
        o.status       = status
        o.filled       = filled or 0.0
        o.remaining    = remaining or 0.0
        o.avgFillPrice = avgFillPrice or 0.0
        o.lastUpdate   = time.time()
        
    def ExecDetails(self, orderId, fillQty, fillPrice):
        o = self.orders.get(orderId)
        if o is None:
            o = ManagedOrder(orderId, meta = {'source' : 'unknown'})
            self.orders[orderId] = o
        
        o.avgFillPrice = fillPrice or o.avgFillPrice
        o.filled = max(o.filled, (fillQty or 0.0))
        o.lastUpdate = time.time()
        
    def Working(self, orderId):
        o = self.orders.get(orderId)
        return (o is not None) and (o.status in workingStatus)
    
    def Done(self, orderId):
        o = self.orders.get(orderId)
        return (o is not None) and (o.status in doneStatus)
    
    def AgeSeconds(self, orderId):
        o = self.orders.get(orderId)
        return (time.time() - o.createTime) if o else 0.0
    
    def Cancel(self, orderId):
        self.tws.cancelOrder(orderId)
        
    def Filled(self, orderId):
        o = self.orders.get(orderId)
        return (o is not None) and (o.status == "Filled")   
    
    def AvgFillPrice(self, orderId):
        o = self.orders.get(orderId)
        return o.avgFillPrice if o else None
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        