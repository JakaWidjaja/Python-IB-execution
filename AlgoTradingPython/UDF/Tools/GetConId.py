from threading import Event


class GetConId:
    def __init__(self):
        pass
    
    def QualifyContract(self, tws, contract, timeout = 5.0):
        reqId = tws.getNextReqId()

        # use twsWrapper's existing containers
        with tws.contractDetailsLock:
            tws.contractDetailsData[reqId] = []
        tws.contractDetailsEndEvent[reqId] = Event()

        tws.reqContractDetails(reqId, contract)

        ok = tws.contractDetailsEndEvent[reqId].wait(timeout=timeout)
        if not ok:
            raise TimeoutError("Timeout waiting for contractDetailsEnd")
        
        with tws.contractDetailsLock:
            matches = tws.contractDetailsData.get(reqId, [])
        
        if len(matches) == 0:
            raise ValueError("Contract qualification failed (0 matches). Check exchange + expiry format.")
        return matches[0].contract