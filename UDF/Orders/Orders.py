from ibapi.client import Order

import time

class Orders:
    def __init__(self, tws, timeDelay):
        self.tws       = tws
        self.timeDelay = timeDelay
        
    #==================================================================================
    #**********************************************************************************
    def SingleMktOrder(self, contract, direction, quantity):
        self.contract  = contract
        self.direction = direction
        self.quantity  = quantity
        
        #Create order object
        orderObject = Order()
        orderObject.action        = self.direction
        orderObject.orderType     = 'MKT'
        orderObject.totalQuantity = self.quantity
        orderObject.eTradeOnly    = ''
        orderObject.firmQuoteOnly = ''
        
        #reqId api updated the nextValidOrderId class variable with the available order id
        self.tws.reqIds(3)
        
        time.sleep(self.timeDelay)
        
        self.tws.placeOrder(self.tws.nextValidOrderId, self.contract, orderObject)
        
    def SingleLmtOrder(self, contract, direction, quantity, limitPrice):
        self.contract   = contract
        self.direction  = direction
        self.quantity   = quantity
        self.limitPrice = limitPrice
        
        #Create order object
        orderObject = Order()
        orderObject.action        = self.direction
        orderObject.orderType     = 'LMT'
        orderObject.totalQuantity = self.quantity
        orderObject.lmtPrice      = self.limitPrice
        orderObject.eTradeOnly    = ''
        orderObject.firmQuoteOnly = ''
        
        #reqId api updated the nextValidOrderId class variable with the available order id
        self.tws.reqIds(3)
        
        time.sleep(self.timeDelay)
        
        self.tws.placeOrder(self.tws.nextValidOrderId, self.contract, orderObject)
        
    def SingleStopOrder(self, contract, direction, quantity, stopPrice):
        self.contract  = contract
        self.direction = direction
        self.quantity  = quantity
        self.stopPrice = stopPrice
        
        #Create order object
        orderObject = Order()
        orderObject.action        = self.direction
        orderObject.orderType     = 'STP'
        orderObject.totalQuantity = self.quantity
        orderObject.auxPrice      = self.stopPrice
        orderObject.eTradeOnly    = ''
        orderObject.firmQuoteOnly = ''
        
        #reqId api updated the nextValidOrderId class variable with the available order id
        self.tws.reqIds(3)
        
        time.sleep(self.timeDelay)
        
        self.tws.placeOrder(self.tws.nextValidOrderId, self.contract, orderObject)
        
    def SingleTrailStopOrder(self, contract, direction, quantity, stopPrice, trailStep = 1):
        self.contract = contract
        self.direction = direction
        self.quantity = quantity
        self.stopPrice = stopPrice
        self.trailStep = trailStep
        
        #Create order object
        orderObject = Order()
        orderObject.action         = self.direction
        orderObject.orderType      = 'TRAIL'
        orderObject.totalQuantity  = self.quantity
        orderObject.auxPrice       = self.trailStep
        orderObject.trailStopPrice = self.stopPrice
        orderObject.eTradeOnly     = ''
        orderObject.firmQuoteOnly  = ''
        
        #reqId api updated the nextValidOrderId class variable with the available order id
        self.tws.reqIds(3)
        
        time.sleep(self.timeDelay)
        
        self.tws.placeOrder(self.tws.nextValidOrderId, self.contract, orderObject)
    #**********************************************************************************   
    #==================================================================================
    
    #==================================================================================
    #**********************************************************************************
    def MultiMktOrder(self, contractList, directionList, quantityList):
        self.contractList  = contractList
        self.directionList = directionList
        self.quantityList  = quantityList
        
        #Set the orderId
        orderId = self.tws.nextValidOrderId
        
        #Length of the list
        lenList = len(self.directionList)
        
        #Create order object
        multiOrder = []
        for i, n in enumerate(self.directionList):
            orderObject = Order()
            orderObject.orderId       = orderId + i
            orderObject.action        = self.directionList[i]
            orderObject.orderType     = 'MKT'
            orderObject.totalQuantity = self.quantityList[i]
            orderObject.eTradeOnly    = ''
            orderObject.firmQuoteOnly = ''
            
            if i == lenList: 
                orderObject.transmit = True
            else:
                #Delay order until all have been committed
                orderObject.transmit = False
                
            multiOrder.append(orderObject)
        
        #reqId api updated the nextValidOrderId class variable with the available order id
        self.tws.reqIds(3)
        
        time.sleep(self.timeDelay)
        
        #Place order
        contracts = list(self.contractList.values())
        for i, mult in enumerate(multiOrder):
            self.tws.placeOrder(mult.orderId, contracts[i], mult)
        
        #**********************************************************************************   
        #==================================================================================
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        