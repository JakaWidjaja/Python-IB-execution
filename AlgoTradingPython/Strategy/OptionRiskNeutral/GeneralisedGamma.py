import numpy as np
from dataclasses import dataclass
from scipy.special import gamma, gammainc  
from scipy.optimize import minimize, brentq

class GeneralisedGamma:
    def __init__(self):
        pass
    
    def hj(self, alpha, xi, j):
        """
        h_j(ξ) = Γ(α + j/ξ) / Γ(α),  j = 1, 2, ...
        """
        return gamma(alpha + j / xi) / gamma(alpha)

    def xiEquation(self, xi, alpha, nu):
        """
        Equation (14): h2(ξ) / h1(ξ)^2 = 1 + ν^2
        Returns left-hand side minus right-hand side.
        """
        h1 = self.hj(alpha, xi, j=1)
        h2 = self.hj(alpha, xi, j=2)
        lhs = h2 / (h1**2)
        rhs = 1.0 + nu**2
        return lhs - rhs
    
    def xiStar(self, alpha, nu):
        """
        Solve equation (14) for ξ given α and ν > 0:
            h2(ξ) / h1(ξ)^2 = 1 + ν^2.

        Uses a simple bracketing + Brent root finder.
        """
        if nu <= 0:
            raise ValueError('nu must be positive')

        a, b = 1e-3, 50.0

        fa = self.xiEquation(a, alpha, nu)
        fb = self.xiEquation(b, alpha, nu)

        if fa * fb > 0:
            b = 200.0
            fb = self.xiEquation(b, alpha, nu)
            if fa * fb > 0:
                raise ValueError('Failed to bracket root for xi. Try different bounds or parameters')

        xi = brentq(self.xiEquation, a, b, args=(alpha, nu))
        return xi

    def GammaCDF(self, z, alpha):
        if z <= 0:
            return 0.0
        return float(gammainc(alpha, z))

    def d(self, price, strike, intRate, expiry, xi, alpha):
        """
        d = ( K e^{-r t} h1(ξ*) / S )^{ξ*}
        """
        discountedStrike = strike * np.exp(-intRate * expiry)

        h1 = self.hj(alpha, xi, j=1)

        base = discountedStrike * h1 / price

        if base <= 0:
            return 0.0
        return base**xi

    def OptionPrice(self, price, strike, expiry, intRate, xi, alpha, optType):
        d_val = self.d(price, strike, intRate, expiry, xi, alpha)

        gAlpha = self.GammaCDF(d_val, alpha)
        gAlphaPlus = self.GammaCDF(d_val, alpha + 1.0 / xi)

        term1 = price * (1.0 - gAlphaPlus)
        term2 = strike * np.exp(-intRate * expiry) * (1.0 - gAlpha)

        call = term1 - term2

        if optType.lower() == 'call':
            return call
        else:
            # Put via put-call parity
            return call + strike * np.exp(-intRate * expiry) - price

    def Calibrate(self, marketPrice, price, strike, expiry, intRate, optType):
        """
        marketPrice : array-like of market option prices
        price       : spot S
        strike      : array-like of strikes
        expiry      : scalar T
        intRate     : scalar r
        optType     : array-like of 'call'/'put' for each strike
        """
        marketPrice = np.asarray(marketPrice)
        strike = np.asarray(strike)

        def error(params):
            xi, alpha = params

            modelPrice = [
                self.OptionPrice(price, k, expiry, intRate, xi, alpha, oType)
                for k, oType in zip(strike, optType)
            ]

            modelPrice = np.asarray(modelPrice)
            sse = np.sum((marketPrice - modelPrice) ** 2)
            return sse

        init = [0.5, 2.0]  # some reasonable starting values

        # Add bounds to keep xi, alpha > 0
        bounds = [(0.1, 13.0), (0.8, 12.0)]
        
        res = minimize(error, init, method='L-BFGS-B', bounds=bounds)
        
        xiHat, alphaHat = res.x
        return xiHat, alphaHat, res
    
    def CalibrationSuccess(self, xi, alpha, res):
        if not res.success:
            return False
        
        if not (np.isfinite(xi) and np.isfinite(alpha)):
            return False
        
        return True