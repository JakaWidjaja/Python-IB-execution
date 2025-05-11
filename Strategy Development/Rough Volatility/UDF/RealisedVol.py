import numpy  as np
import pandas as pd
from scipy.linalg import toeplitz, cholesky
from scipy.optimize import minimize

class RoughVolatility:
    def __init__(self):
        pass
    
    def RealisedVolatility(self, prices, window = 1):
        self.prices = prices
        self.window = window
        
        logReturns = np.log(prices[1: ] / prices[:-1])
        realisedVariance = pd.series(logReturns**2).rolling(window = self.window).mean()
        return np.sqrt(realisedVariance)
        
    
    def FractionalBrownianMotion(self, h, n, deltat = 1):
        self.h      = h
        self.n      = n 
        self.deltat = deltat
        
        times = np.arange(0, self.n * self.deltat, self.deltat)
        covMatrix = 0.5 * (np.abs(times[:, None]) **(2 * self.h) + np.abs(times[None, :]) ** (2 * self.h) - \
                           np.abs(times[:, None] - times[None, :])**(2*self.h))
            
        L = cholesky(covMatrix, lower = True)
        Z = np.random.normal(size = self.n)
        fbm = np.dot(L, Z)
        
        return fbm
    
    def FractionalOU(self, h, nu, alpha, n, deltat = 1):
        self.h      = h
        self.nu     = nu
        self.alpha  = alpha
        self.n      = n
        self.deltat = deltat
        
        fbm = self.FractionalBrownianMotion(self.h, self.n, self.deltat)
        OUProcess = np.zeros(self.n)
        for t in range(1, self.n):
            OUProcess[t] = OUProcess[t-1] * np.exp(-self.alpha * self.deltat) + self.nu * fbm[t]
        return OUProcess
    
    def Calibration(self, realisedVols, deltat = 1):
        self.realisedVols = realisedVols
        self.deltat       = deltat
        
        logRealisedVol = np.log(self.realisedVols)
        n = len(self.realisedVols)
        
        def error(params):
            h, nu, alpha = params
            if h <= 0 or h >= 0.5 or nu <= 0.5 or alpha <= 0:
                return np.inf
            
            simulatedOU = self.fractionalOU(h, nu, alpha, n, self.deltat)
            return np.mean((logRealisedVol - simulatedOU)**2)
        
        init = [0.1, 0.1, 0.01]
        bnds = ((0.01, 0.5), (0.01, None), (0.001, None))
        res = minimize(error, init, bounds = bnds)
        
        return res.x
    
    def Forecast(self, h, nu, alpha, currentVol, horizon, deltat = 1):
        self.h = h
        self.nu = nu
        self.alpha = alpha
        self.currentVol = currentVol
        self.horizon = horizon
        self.deltat = deltat
        
        OUProcess = self.FractionalOU(self.h, self.nu, self.alpha, self.horizon)
        logFutureVols = np.log(self.currentVol**2) + OUProcess
        futureVols = np.exp(logFutureVols / 2.0)
        return futureVols
        
if __name__ == "__main__":
    # Generate a synthetic time series of stock prices
    np.random.seed(42)
    stock_prices = np.exp(np.cumsum(np.random.normal(0, 0.02, 500)))

    # Calculate realized volatility
    realized_vols = realisedVol(stock_prices, window=10)
    realized_vols = realized_vols.dropna().values

    # Calibrate Hurst exponent, vol of vol, and mean-reversion rate
    H, nu, alpha = calibrate_params(realized_vols)
    print(f"Calibrated Hurst Exponent: {H}, Vol of Vol: {nu}, Mean Reversion Rate: {alpha}")

    # Forecast future realized volatility
    current_vol = realized_vols[-1]
    forecast_horizon = 20
    future_vols = forecast_realized_volatility(H, nu, alpha, current_vol, forecast_horizon)
    print("Forecasted Future Realized Volatility:")
    print(future_vols)        
    
    