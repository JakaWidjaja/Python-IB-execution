import numpy as np
from scipy.special import erf
from hmmlearn.hmm import GaussianHMM

class HMM:
    def __init__(self, numStates = 2):
        self.numStates = numStates
        self.model = GaussianHMM(n_components = self.numStates, covariance_type = 'diag', n_iter = 5000,  init_params="st")
        
    def Fit(self, prices):
        self.prices = prices #numpy array
        
        self.logPrices = np.log(prices)
        
        self.returns = np.diff(self.logPrices).reshape(-1,1)
        self.returns = (self.returns - np.mean(self.returns)) / np.std(self.returns)  # Normalize
        
        self.model.means_ = np.array([[0.01], [-0.01]])  # Initial guess for means
        self.model.covars_ = np.array([[0.02], [0.03]])  # Initial guess for variances
        
        self.model.fit(self.returns)
        
        
        
    def PredictStates(self):
        self.hiddenStates = self.model.predict(self.returns)
        return self.hiddenStates
    
    def SimulatePrice(self, startPrice, numSimulation = 100):
        self.startPrice    = startPrice
        self.numSimulation = numSimulation 
        
        means = self.model.means_.flatten()
        variances = np.sqrt(self.model.covars_).flatten()
        transitionMatrix = self.model.transmat_
        
        prices = [self.startPrice]
        currentState = self.hiddenStates[-1]
        
        for _ in range(self.numSimulation):
            nextState = np.random.choice(self.numStates, p = transitionMatrix[currentState])
            drift = means[nextState]
            volatility = variances[nextState]
            simulatedReturn = np.random.normal(drift, volatility)
            prices.append(prices[-1] * np.exp(simulatedReturn))
            currentState = nextState
            
        return np.array(prices)
    
    def ConfidenceIntervals(self, prices, ciLevel = 0.95):
        self.prices  = prices
        self.ciLevel = ciLevel
        
        zScore = {0.90 : 1.645, 
                  0.95 : 1.960, 
                  0.99 : 2.576}.get(self.ciLevel, 1.960)
        
        means = self.model.means_.flatten()
        variances = np.sqrt(self.model.covars_).flatten()
        
        lowerBound = []
        upperBound = []
        
        for i, state in enumerate(self.hiddenStates):
            mean = means[state]
            stDev = variances[state]
            lBound = prices[i] * np.exp(mean - zScore * stDev)
            uBound = prices[i] * np.exp(mean + zScore * stDev)
            lowerBound.append(lBound)
            upperBound.append(uBound)
            
        return np.array(lowerBound), np.array(upperBound)
    
    def OptionPrice(self, strike, rate, expiry):
        self.strike = strike
        self.rate   = rate
        self.expiry = expiry
        
        means = self.model.means_.flatten()
        variances = np.sqrt(self.model.covars_.flatten())
        transitionMatrix = self.model.transmat_
        
        expectedPrice = 0.0
        for state in range(self.numStates):
            stateProb  = np.mean(self.hiddenStates == state)
            drift      = means[state]
            volatility = variances[state]
            
            # Calculate expeted stock price at mturity
            expectedStockPrice = np.exp(drift * self.expiry - 0.5 * volatility**2 * self.expiry)
            expectedStockPrice = np.exp(drift * self.expiry + volatility * np.sqrt(self.expiry))
            
            # Black-Scholes formula for call option
            d1 = (np.log(expectedStockPrice / self.strike) + (self.rate + 0.5 * volatility**2) * self.expiry) / (volatility * np.sqrt(self.expiry))
            d2 = d1 - volatility * np.sqrt(self.expiry)
            
            optionPrice = expectedStockPrice * self.NormCDF(d1) - self.strike * np.exp(-self.rate * self.expiry) * self.NormCDF(d2)
            
            expectedPrice += stateProb * optionPrice
            print(f"State: {state}, Probability: {stateProb:.4f}, Drift: {drift:.4f}, Volatility: {volatility:.4f}")
            print(f"Expected Stock Price: {expectedStockPrice:.4f}")
            print(f"d1: {d1:.4f}, d2: {d2:.4f}")
            
        return expectedPrice
    
    @staticmethod
    def NormCDF(x):

        return (1.0 + erf(x / np.sqrt(2.0))) / 2.0
            
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    
    # Example stock prices (replace with real data)
    prices = np.array([100, 102, 101, 104, 107, 105, 110, 108, 112, 115])
    
    # Initialize and fit the model
    model = HMM(numStates = 2)
    model.Fit(prices)
    
    # Predict hidden states
    hiddenStates = model.PredictStates()
    
    # Simulate future stock prices
    simulatedPrices = model.SimulatePrice(prices[-1], 30)
    
    #Calculate option price
    optionPrice = model.OptionPrice(strike = 110, rate = 0.05, expiry = 1)
    
    
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        