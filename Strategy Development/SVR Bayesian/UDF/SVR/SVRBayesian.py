import numpy as np
from sklearn.svm import SVR
from sklearn.preprocessing import MinMaxScaler
from scipy.optimize import minimize
import GPyOpt

class SVRBayesian:
    def __init__(self, kernel = 'rbf', error = 0.1, gamma = 'scale', scalingRange = (0.1, 10)):
        self.kernel       = kernel          #Kernel type for SVR. Default is 'rbf'.
        self.error        = error           #Limit of loss function
        self.gamma        = gamma           #Kernel coefficient for 'rbf', 'poly', and 'sigmoid'
        self.scalingRange = scalingRange    #Range for the scaling parameter µ.
        self.scaler       = MinMaxScaler()
        self.svr          = None
        self.mu           = None
        
    def ScaleFeature(self, x, y):
        self.x = x
        self.y = y
        
        xScaled = self.scaler.fit_transform(self.x)
        
        yMin, yMax = min(y), max(y)
        yScaled    = (y - yMin) / (yMax - yMin)
        
        return xScaled, yScaled, yMin, yMax
    
    def InverseScaleTarget(self, yScaled, yMin, yMax):
        self.yScaled = yScaled
        self.yMin    = yMin
        self.yMax    = yMax
        
        return self.yScaled * (self.yMax - self.yMin) + self.yMin
    
    def EvidenceFunc(self, params, x, y):
        self.params = params
        self.x      = x
        self.y      = y
        
        c, epsilon, mu = params
        gamma = self.gamma if isinstance(self.gamma, str) else self.gamma * mu
        
        self.svr = SVR(kernel = self.kernel, C = c, epsilon = epsilon, gamma = gamma)
        self.svr.fit(self.x, self.y)
        
        yPred = self.svr.predict(x)
        residuals = y - yPred
        
        # Evidence as negative log-likelihood approximation
        evidence = -np.sum(np.log(1 / (2 * np.sqrt(np.pi * mu)) * np.exp(-residuals**2 / (2 * mu))))
        
        return evidence
    
    def OptimiseParams(self, x, y):
        self.x = x
        self.y = y
        
        bounds = [ {'name': 'C'      , 'type': 'continuous', 'domain': (0.1, 100)},
                   {'name': 'epsilon', 'type': 'continuous', 'domain': (0.01, 1)},
                   {'name': 'mu'     , 'type': 'continuous', 'domain': self.scalingRange}  ]
        
        def ObjFunc(params):
            params = params[0]
            return self.EvidenceFunc(params, self.x, self.y)
        
        optimiser = GPyOpt.methods.BayesianOptimization(f = ObjFunc, domain = bounds)
        optimiser.run_optimization(max_iter = 50)
        
        return optimiser.x_opt
    
    def Fit(self, x, y):
        self.x = x
        self.y = y
    
        xScaled, yScaled, yMin, yMax = self.ScaleFeature(self.x, self.y)
        
        #Optimised parameter
        optParams = self.OptimiseParams(xScaled, yScaled)
        self.mu   = optParams[2]
        
        #Train the final SVR with optimised parameters
        c, epsilon = optParams[0], optParams[1]
        gamma = self.gamma if isinstance(self.gamma, str) else self.gamma * self.mu
        
        self.svr = SVR(kernel = self.kernel, C = c, epsilon = epsilon, gamma = gamma)
        self.svr.fit(xScaled, yScaled)
        
        self.yMin = yMin
        self.yMax = yMax
        
    def predict(self, x):
        self.x = x
        
        xScaled = self.scaler.transform(self.x)
        yPredScaled = self.svr.predict(xScaled)
        
        return self.InverseScaleTarget(yPredScaled, self.yMin, self.yMax)
        
if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from sklearn.model_selection import train_test_split
    import time
    
    # Generate synthetic time-series data
    np.random.seed(42)
    n_samples = 200
    time_series = np.sin(np.linspace(0, 10, n_samples)) + np.random.normal(0, 0.1, n_samples)
    
    # Create lagged features
    def create_lagged_features(data, lag=5):
        X, y = [], []
        for i in range(len(data) - lag):
            X.append(data[i:i+lag])
            y.append(data[i+lag])
        return np.array(X), np.array(y)
    
    lag = 30
    X, y = create_lagged_features(time_series, lag)
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    
    # Use the BayesianSVR class
    model = SVRBayesian()
    
    start = time.time()
    model.Fit(X_train, y_train)
    end = time.time()
    print(end - start)
    
    # Predictions
    y_pred = model.predict(X_test)
    
    # Plot actual vs predicted values
    plt.figure(figsize=(8, 6))
    plt.plot(y_test, label="Actual", marker="o")
    plt.plot(y_pred, label="Predicted", marker="x")
    plt.xlabel("Sample Index")
    plt.ylabel("Value")
    plt.title("Actual vs Predicted Values")
    plt.legend()
    plt.show()
    
    plt.plot(time_series)
    plt.plot(X)
    plt.plot(y)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    