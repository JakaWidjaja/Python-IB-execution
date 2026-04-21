from threading import Event
from collections import Counter

class OptionChain:
    def __init__(self, enableCache=True):
        self.enableCache = enableCache
        self.cache = {}

    def InferStepNearATM(self, strikesSorted, futuresPrice, window=40):
        if not strikesSorted:
            return None

        futuresPrice = float(futuresPrice)
        strikesSorted = [float(x) for x in strikesSorted]

        atmIndex = min(range(len(strikesSorted)), key=lambda i: abs(strikesSorted[i] - futuresPrice))

        lo = max(0, atmIndex - window // 2)
        hi = min(len(strikesSorted) - 1, atmIndex + window // 2)

        diffs = []
        for i in range(lo, hi):
            d = strikesSorted[i + 1] - strikesSorted[i]
            if d > 0:
                diffs.append(round(float(d), 6))

        if not diffs:
            return None

        step, _ = Counter(diffs).most_common(1)[0]
        return float(step)

    def GetATMBand(self, strikesSorted, futuresPrice, numAroundATM=10, stepHint=None):
        if not strikesSorted:
            return [], None, None

        futuresPrice = float(futuresPrice)
        strikesSorted = [float(x) for x in strikesSorted]

        atm = min(strikesSorted, key=lambda k: abs(k - futuresPrice))

        step = float(stepHint) if stepHint is not None else self.InferStepNearATM(strikesSorted, futuresPrice)

        if step is None:
            diffs = [b - a for a, b in zip(strikesSorted[:-1], strikesSorted[1:]) if (b - a) > 0]
            step = min(diffs) if diffs else 1.0

        band = [atm + step * i for i in range(-numAroundATM, numAroundATM + 1)]
        bandSet = set(band)
        bandList = [k for k in strikesSorted if k in bandSet]

        return bandList, atm, step

    def QualifyContract(self, tws, contract, timeout=5.0):
        if getattr(contract, "conId", 0) not in (0, None):
            return contract

        reqId = tws.getNextReqId()
        tws.contractDetailsData[reqId] = []
        tws.contractDetailsEndEvent[reqId] = Event()

        tws.reqContractDetails(reqId, contract)

        if not tws.contractDetailsEndEvent[reqId].wait(timeout=timeout):
            raise TimeoutError(f"reqContractDetails timed out after {timeout}s (reqId={reqId})")

        details = tws.contractDetailsData.get(reqId, [])
        if not details:
            raise ValueError("No contractDetails returned (invalid/ambiguous contract)")

        qualified = details[0].contract
        contract.conId = qualified.conId
        contract.exchange = qualified.exchange or contract.exchange
        return contract

    def GetChain(self, tws, *, underlyingContract, underlyingSymbol, fopExchange = "CME", underlyingSecType = "FUT",
                     tradingClass = None, multiplier = None, includeExpiries = None, timeout = 8.0):
        key = (getattr(underlyingContract, "conId", 0),
               underlyingSymbol,
               fopExchange,
               underlyingSecType,
               tradingClass,
               multiplier)

        if self.enableCache and key in self.cache:
            strikesSorted, expiriesSorted, rows = self.cache[key]
        else:
            underlyingContract = self.QualifyContract(tws, underlyingContract, timeout=timeout)

            reqId = tws.getNextReqId()
            tws.secDefOptParams[reqId] = []
            tws.secDefOptParamsComplete[reqId] = Event()

            tws.reqSecDefOptParams(reqId,
                                   underlyingSymbol,
                                   fopExchange,
                                   underlyingSecType,
                                   int(underlyingContract.conId))

            if not tws.secDefOptParamsComplete[reqId].wait(timeout=timeout):
                raise TimeoutError(f"reqSecDefOptParams timed out after {timeout}s "
                                   f"(reqId = {reqId}, symbol = {underlyingSymbol}, conId = {underlyingContract.conId})")

            rows = tws.secDefOptParams.get(reqId, [])
            if not rows:
                raise ValueError(f"No option-chain rows returned (reqId={reqId})")

            # Filter rows properly
            filtered = rows
            if tradingClass is not None:
                filtered = [r for r in filtered if r.get("tradingClass") == tradingClass]
            if multiplier is not None:
                filtered = [r for r in filtered if str(r.get("multiplier")) == str(multiplier)]
            if not filtered:
                filtered = rows

            strikes = set()
            expiries = set()
            for r in filtered:
                strikes  |= set(r.get("strikes", []))
                expiries |= set(r.get("expirations", []))

            strikesSorted = sorted(float(s) for s in strikes)
            expiriesSorted = sorted(expiries)
            rows = filtered

            if self.enableCache:
                self.cache[key] = (strikesSorted, expiriesSorted, rows)

        if includeExpiries is not None:
            includeSet = {str(e).strip() for e in includeExpiries if str(e).strip()}
            expiriesSorted = [e for e in expiriesSorted if e in includeSet]
            if not expiriesSorted:
                raise ValueError(f"No matching expiries found for includeExpiries={sorted(includeSet)}")

        return strikesSorted, expiriesSorted, rows

    def GetATMStrikeBand(self, tws, *, underlyingContract, underlyingSymbol, futuresPrice, includeExpiries = None,
                         fopExchange = "CME", underlyingSecType = "FUT", tradingClass = None, multiplier = None,
                         numAroundATM = 10, stepHint = None, timeout = 5.0):
        
        strikesSorted, expiriesSorted, rows = self.GetChain(tws,
                                                            underlyingContract = underlyingContract,
                                                            underlyingSymbol   = underlyingSymbol,
                                                            fopExchange        = fopExchange,
                                                            underlyingSecType  = underlyingSecType,
                                                            tradingClass       = tradingClass,
                                                            multiplier         = multiplier,
                                                            includeExpiries    = includeExpiries,
                                                            timeout            = timeout)

        band, atm, step = self.GetATMBand(strikesSorted,
                                          futuresPrice = futuresPrice,
                                          numAroundATM = numAroundATM,
                                          stepHint     = stepHint)

        return band, expiriesSorted, {"atm": atm, "step": step, "rows": rows}
