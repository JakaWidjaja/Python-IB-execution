class CashAmount:
    def __init__(self, tws):
        self.tws = tws
    
    def SafeFloat(self, x, default = 0.0):
        try:
            return float(x)
        except Exception:
            return default
        
    def GetAccountValueUSD(self, tags, prefer_tags, timeout=2.0):
        """
        Request account summary, then read a USD value using preferred tags list.
        """
        try:
            self.tws.reqAccountValue(tags = tags, timeout = timeout)
        except Exception:
            pass
    
        df = getattr(self.tws, "dfAccountValues", None)
        if df is None or df.empty:
            return None
    
        df2 = df.copy()
        df2["currency"] = df2["currency"].astype(str).str.upper()
        
        usd = df2[df2["currency"].eq("USD")]
        base_or_blank = df2[df2["currency"].isin(["", "BASE", "USDOLLAR", "US DOLLAR"])]
        
        # search USD first, then fallback
        for tag in prefer_tags:
            rows = usd[usd["tag"] == tag]
            if not rows.empty:
                return self.SafeFloat(rows.iloc[-1]["value"], None)
        
        for tag in prefer_tags:
            rows = base_or_blank[base_or_blank["tag"] == tag]
            if not rows.empty:
                return self.SafeFloat(rows.iloc[-1]["value"], None)
        
        return None

    def GetUSDCash(self, timeout = 2.0):
        """
        Return (cash_value, currency) for CashBalance/TotalCashBalance.
        Prefer USD if present, otherwise return whatever currency IB provides.
        """
        try:
            self.tws.reqAccountValue(tags="$LEDGER", timeout=timeout)
        except Exception:
            pass
    
        df = getattr(self.tws, "dfAccountValues", None)
        if df is None or df.empty:
            return (0.0, None)
    
        df2 = df.copy()
        df2["currency"] = df2["currency"].astype(str).str.upper()
    
        # prefer USD cash if IB actually returns it
        for tag in ["CashBalance", "TotalCashBalance"]:
            rows = df2[(df2["tag"] == tag) & (df2["currency"] == "USD")]
            if not rows.empty:
                r = rows.iloc[-1]
                return (self.SafeFloat(r["value"], 0.0), "USD")
    
        # fallback: any currency (AUD base accounts often show AUD only)
        for tag in ["CashBalance", "TotalCashBalance"]:
            rows = df2[df2["tag"] == tag]
            if not rows.empty:
                r = rows.iloc[-1]
                return (self.SafeFloat(r["value"], 0.0), str(r["currency"]))
    
        return (0.0, None)
    
    def GetUSDAvailableFunds(self, timeout=2.0):
        """
        Return (value, currency) for AvailableFunds (fallback to ExcessLiquidity/BuyingPower).
        """
        try:
            self.tws.reqAccountValue(tags="AvailableFunds,ExcessLiquidity,BuyingPower,NetLiquidation", timeout=timeout)
        except Exception:
            pass
    
        df = getattr(self.tws, "dfAccountValues", None)
        if df is None or df.empty:
            return (0.0, None)
    
        for t in ["AvailableFunds", "ExcessLiquidity", "BuyingPower"]:
            rows = df[df["tag"] == t]
            if not rows.empty:
                r = rows.iloc[-1]
                return (self.SafeFloat(r["value"], 0.0), str(r["currency"]))
        return (0.0, None)
    
    def GetComboMultiplier(self, optionContracts, signalDict, defaultMult=50.0):
        """
        Try read multiplier from any leg contract; fallback to 50 (ES).
        """
        if not isinstance(signalDict, dict):
            return float(defaultMult)
    
        for key, strike in signalDict.items():
            if key in ("direction", "limit price", "numContract"):
                continue
            try:
                directionLeg, optType, idx = key.split(" ")
            except Exception:
                continue
    
            try:
                k = str(int(float(strike)))
            except Exception:
                k = str(strike)
    
            lookup = f"{optType}_{k}"
            c = optionContracts.get(lookup)
            if c is not None:
                m = getattr(c, "multiplier", None)
                if m is not None and str(m).strip() != "":
                    return float(m)
                break
    
        return float(defaultMult)
    
    def LegsFromSignal(self, signalDict):
        """
        Convert signal to list of legs: (optType, strike, weight)
        weight: +1 for 'long', -1 for 'short'
        """
        legs = []
        for key, strike in signalDict.items():
            if key in ("direction", "limit price", "numContract"):
                continue
            try:
                ls, optType, idx = key.split(" ")
            except Exception:
                continue
    
            w = +1.0 if ls.lower() == "long" else -1.0
            legs.append((optType.lower(), float(strike), w))
        return legs

    def Intrinsic(self, optType, S, K):
        if optType == "call":
            return max(S - K, 0.0)
        else:
            return max(K - S, 0.0)
    
    def EstimateButterflyMarginUSD(self, signalDict, optionContracts, qty=1, buffer=1.10):
        """
        Conservative margin estimate for SELL of the BAG:
          required ~= max_loss_usd * buffer
        We compute max loss by evaluating payoff at key breakpoints (strikes and extremes).
        """
        if not isinstance(signalDict, dict) or not signalDict:
            return float("inf")
    
        direction = str(signalDict.get("direction", "")).upper()
        if direction not in ("BUY", "SELL"):
            return float("inf")
    
        # premium in points (IB lmtPrice is positive; BUY pays it, SELL receives it)
        premium = self.SafeFloat(signalDict.get("limit price", 0.0), 0.0)
        legs    = self.LegsFromSignal(signalDict)
        if not legs:
            return float("inf")
    
        strikes = sorted({K for _, K, _ in legs})
        kmin, kmax = strikes[0], strikes[-1]
        span = max(kmax - kmin, 1.0)
    
        # evaluate at breakpoints; butterflies are piecewise linear so this is enough
        test_points = [kmin - 2.0 * span] + strikes + [kmax + 2.0 * span]
    
        def PayoffLongStructure(S):
            # payoff of being long the structure defined by legs (long legs +, short legs -)
            p = 0.0
            for optType, K, w in legs:
                p += w * self.Intrinsic(optType, S, K)
            return p
    
        # profit in points
        # BUY:  +payoff - premium
        # SELL: -payoff + premium
        profits = []
        for S in test_points:
            payoff = PayoffLongStructure(S)
            if direction == "BUY":
                prof = payoff - premium
            else:
                prof = -payoff + premium
            profits.append(prof)
    
        # max loss in points
        maxLossPts = max(0.0, -min(profits))
    
        mult = self.GetComboMultiplier(optionContracts, signalDict, defaultMult=50.0)
        req = maxLossPts * mult * int(qty)
        return float(req) * float(buffer)
    
    def EstimateButterflyDebitUSD(self, signalDict, optionContracts, qty=1, buffer=1.10, defaultMult=50.0):
        """
        Required USD cash for BUY butterfly ≈ debit * multiplier * qty * buffer.
        debit is signalDict['limit price'] in index points (e.g. 1.25).
        """
        if not isinstance(signalDict, dict) or not signalDict:
            return float("inf")
    
        direction = str(signalDict.get("direction", "")).upper()
        if direction != "BUY":
            return float("inf")
    
        debitPts = self.SafeFloat(signalDict.get("limit price", 0.0), 0.0)
        mult = self.GetComboMultiplier(optionContracts, signalDict, defaultMult = defaultMult)
    
        return abs(debitPts) * mult * int(qty) * float(buffer)
    
    def GetCashByCurrency(self, ccy = 'USD', timeout = 3.0):
        df = getattr(self.tws, 'dfAccountValues', None)
        if df is None or df.empty:
            return 0.0
        
        rows = df[(df['tag'].isin(['CashBalance', 'TotalCashBalance'])) & (df['currency'].astype(str).str.upper() == ccy)]
        
        if rows.empty:
            return 0.0
        return self.SafeFloat(rows.iloc[-1]['value'], 0.0)