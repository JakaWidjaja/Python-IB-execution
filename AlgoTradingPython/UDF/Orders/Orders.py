from ibapi.order  import Order
from UDF.Contract import MakeContract

class Orders:
    def __init__(self, tws, timeout = 5.0):
        self.tws        = tws
        self.timeout    = timeout
        self.mkContract = MakeContract.MakeContract()
        
    #==================================================================================
    #**********************************************************************************
    def SingleMktOrder(self, contract, direction, quantity):        
        #Create order object
        orderObject = Order()
        orderObject.action        = direction
        orderObject.orderType     = 'MKT'
        orderObject.totalQuantity = quantity
        orderObject.eTradeOnly    = ''
        orderObject.firmQuoteOnly = ''
        
        self.tws.orderIdEvent.clear()
        self.tws.reqIds(-1)
        
        if not self.tws.orderIdEvent.wait(self.timeout):
            raise TimeoutError('next Valid Id not received')
        
        self.tws.placeOrder(self.tws.nextValidOrderId, contract, orderObject)
        self.tws.nextValidOrderId += 1
        
    def SingleLmtOrder(self, contract, direction, quantity, limitPrice):        
        #Create order object
        orderObject = Order()
        orderObject.action        = direction
        orderObject.orderType     = 'LMT'
        orderObject.totalQuantity = quantity
        orderObject.lmtPrice      = limitPrice
        orderObject.eTradeOnly    = ''
        orderObject.firmQuoteOnly = ''
        
        self.tws.orderIdEvent.clear()
        self.tws.reqIds(-1)
        
        if not self.tws.orderIdEvent.wait(self.timeout):
            raise TimeoutError('next Valid Id not received')
        
        self.tws.placeOrder(self.tws.nextValidOrderId, contract, orderObject)
        self.tws.nextValidOrderId += 1
        
    def SingleStopOrder(self, contract, direction, quantity, stopPrice):        
        #Create order object
        orderObject = Order()
        orderObject.action        = direction
        orderObject.orderType     = 'STP'
        orderObject.totalQuantity = quantity
        orderObject.auxPrice      = stopPrice
        orderObject.eTradeOnly    = ''
        orderObject.firmQuoteOnly = ''
        
        self.tws.orderIdEvent.clear()
        self.tws.reqIds(-1)
        
        if not self.tws.orderIdEvent.wait(self.timeout):
            raise TimeoutError('next Valid Id not received')
        
        self.tws.placeOrder(self.tws.nextValidOrderId, contract, orderObject)
        self.tws.nextValidOrderId += 1
        
    def SingleTrailStopOrder(self, contract, direction, quantity, stopPrice, trailStep = 1):
        #Create order object
        orderObject = Order()
        orderObject.action         = direction
        orderObject.orderType      = 'TRAIL'
        orderObject.totalQuantity  = quantity
        orderObject.auxPrice       = trailStep
        orderObject.trailStopPrice = stopPrice
        orderObject.eTradeOnly     = ''
        orderObject.firmQuoteOnly  = ''
        
        self.tws.orderIdEvent.clear()
        self.tws.reqIds(-1)
        
        if not self.tws.orderIdEvent.wait(self.timeout):
            raise TimeoutError('next Valid Id not received')
        
        self.tws.placeOrder(self.tws.nextValidOrderId, contract, orderObject)
        self.tws.nextValidOrderId += 1
    #**********************************************************************************   
    #==================================================================================
    
    #==================================================================================
    #**********************************************************************************
    def MultiMktOrder(self, contractList, directionList, quantityList):
        if not (len(contractList) == len(directionList) == len(quantityList)):
            raise ValueError("contractList, directionList, quantityList must have same length")


        # request fresh order id
        self.tws.orderIdEvent.clear()
        self.tws.reqIds(-1)
    
        if not self.tws.orderIdEvent.wait(self.timeout):
            raise TimeoutError("nextValidId not received")
    
        baseOrderId = self.tws.nextValidOrderId
    
        contracts = list(contractList.values())
    
        for i in range(len(directionList)):
            orderObject = Order()
            orderObject.orderId = baseOrderId + i
            orderObject.action = directionList[i]
            orderObject.orderType = "MKT"
            orderObject.totalQuantity = quantityList[i]
            orderObject.eTradeOnly = ""
            orderObject.firmQuoteOnly = ""
    
            # only transmit on the last one (if you're batching)
            orderObject.transmit = (i == len(directionList) - 1)
    
            self.tws.placeOrder(orderObject.orderId, contracts[i], orderObject)
    
        # reserve that block so next call doesn't reuse ids
        self.tws.nextValidOrderId = baseOrderId + len(directionList)
        
    #**********************************************************************************   
    #==================================================================================
        
    def ButterflyLmtOrder(self, optionContractData, signal, numContract, limitPrice):
        '''
        optionContractData - dict of option contracts, keyed like 'put_6750', 'call_6800'
        signal             - dict describing strikes for each leg + overall direction
        numContract        - number of butterflies
        limitPrice         - NET limit price for the spread
        '''
        portDirection = signal.get('direction', 'BUY').upper()

        # Store legs explicitly (do NOT overwrite by 'long'/'short')
        contractDict = {}
    
        for key, strike in signal.items():
            if key in ('direction', 'limit price'):
                continue
    
            # key: 'long put 1' -> direction='long', optType='put', idx='1'
            direction, optType, idx = key.split(' ')
    
            # pick the contract from the big list
            strike = str(int(strike))
            lookupKey = f'{optType}_{strike}'
            if lookupKey not in optionContractData:
                raise KeyError(f"Missing contract: {lookupKey}")
    
            contractDict[key] = optionContractData[lookupKey]
    
        # Use first leg for symbol/currency
        firstLeg = next(iter(contractDict.values()))
        symbol   = firstLeg.symbol
        currency = firstLeg.currency
    
        # Create BAG
        bag = self.mkContract.MakeButterflyContract(contractDict, symbol, currency)
    
        # Create order
        orderObject = Order()
        orderObject.action        = portDirection
        orderObject.orderType     = 'LMT'
        orderObject.totalQuantity = int(numContract)
        orderObject.lmtPrice      = float(limitPrice)
        orderObject.eTradeOnly    = ''
        orderObject.firmQuoteOnly = ''
        orderObject.transmit      = True
    
        # request order id
        self.tws.orderIdEvent.clear()
        self.tws.reqIds(-1)
    
        if not self.tws.orderIdEvent.wait(self.timeout):
            raise TimeoutError("nextValidId not received")
            
        orderId = self.tws.nextValidOrderId
        self.tws.placeOrder(orderId, bag, orderObject)
        self.tws.nextValidOrderId += 1
        
        return orderId
    
    def ButterflyMktOrder(self, optionContractData, signal, numContract, direction = None):
        '''
        Market order for a butterfly (BAG)
        OptionContractData - dict of option contracts, e.g., 'put_6750', 'call_6800'
        signal             - dict describing strikes for each leg + overall direction
        numContract        - number of butterflies
        direction          - optional override ('BUY'/'SELL'). If none use signal['direction']
        '''
        
        portDirection = (direction or signal.get('direction', 'BUY')).upper()
        
        contractDict = {}
        
        for key, strike in signal.items():
            if key in ('direction', 'limit price', 'numContract'):
                continue
            
            directionLeg, optType, index = key.split(' ')
            strike = str(int(strike))
            lookupKey = f'{optType}_{strike}'
            if lookupKey not in optionContractData:
                raise KeyError(f'Missing contract: {lookupKey}')
                
            contractDict[key] = optionContractData[lookupKey]
            
        firstLeg = next(iter(contractDict.values()))
        symbol = firstLeg.symbol
        currency = firstLeg.currency
        
        bag = self.mkContract.MakeButterflyContract(contractDict, symbol, currency)
        
        orderObject = Order()
        orderObject.action        = portDirection
        orderObject.orderType     = 'MKT'
        orderObject.totalQuantity = int(numContract)
        orderObject.eTradeOnly    = ''
        orderObject.firmQuoteOnly = ''
        orderObject.transmit      = True
        
        self.tws.orderIdEvent.clear()
        self.tws.reqIds(-1)
        
        if not self.tws.orderIdEvent.wait(self.timeout):
            raise TimeoutError('nextValidId not received')
            
        orderId = self.tws.nextValidOrderId
        self.tws.placeOrder(orderId, bag, orderObject)
        self.tws.nextValidOrderId += 1
        
        return orderId
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        