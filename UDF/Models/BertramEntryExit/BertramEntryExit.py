import numpy as np
from scipy.special import factorial, gamma, digamma
from scipy.optimize import minimize

class BertramEntryExit:
    def __init__(self):
        pass
    #Calibration function.
    def CalibrateModel(self, costPrice, guessEntry, guessExit, mu, theta, sigma):
        self.costPrice  = costPrice
        self.guessEntry = guessEntry
        self.guessExit  = guessExit
        self.mu         = mu
        self.theta      = theta
        self.sigma      = sigma
        
        eta = sigma
        x0 = [self.guessEntry, self.guessExit]
        
        cons = [{'type' : 'ineq', 'fun' : self.Constraint1, 'args' : (self.costPrice, eta, self.mu, self.theta, self.sigma)}, 
                {'type' : 'ineq', 'fun' : self.Constraint2, 'args' : (self.costPrice, self.mu, self.theta, self.sigma)},
                {'type' : 'ineq', 'fun' : self.Constraint3, 'args' : (self.mu, self.theta, self.sigma)}]
        
        bnd = [(0, 1), (0, 1)]
        
        #Define a callback function to adjust x0 if guessEntry == guessExit
        def callBack(xk):
            if np.isclose(xk[0], xk[1]):
                xk[1] += 1e-4 #adjust exit price if entry and exit are equal
        
        res = minimize(self.Objective, x0, method = 'SLSQP', 
                       args        = (self.costPrice, self.mu, self.theta, self.sigma), 
                       constraints = cons, 
                       bounds      = bnd, 
                       callback    = callBack)
        
        exitPrice  = np.sqrt((self.sigma**2) / (2.0 * self.theta)) * res.x[1] + self.mu
        entryPrice = np.sqrt((self.sigma**2) / (2.0 * self.theta)) * res.x[0] + self.mu
        
        return [entryPrice, exitPrice]

        
    #Calibration objective to maximise ZM
    def Objective(self, x, costPrice, mu, theta, sigma):
        self.x         = x
        self.costPrice = costPrice
        self.mu        = mu
        self.theta     = theta
        self.sigma     = sigma
        
        entryPrice = self.x[0]
        exitPrice  = self.x[1]
        
        const = np.sqrt(2 * self.theta / (self.sigma**2))
        
        entryPriceAdjust = const * (entryPrice - self.mu)
        exitPriceAdjust  = const * (exitPrice  - self.mu)
        
        return -self.ZM(entryPriceAdjust, exitPriceAdjust, self.costPrice, self.mu, self.theta, self.sigma) * 1e5
    
    #Calibration constrains
    #Variance limit. Variance less than eta. 
    def Constraint1(self, x, costPrice, eta, mu, theta, sigma):
        self.x          = x
        self.constPrice = costPrice
        self.eta        = eta
        self.mu         = mu
        self.theta      = theta
        self.sigma      = sigma
        
        entryPrice = self.x[0]
        exitPrice  = self.x[1]
        
        const = np.sqrt(2.0 * self.theta / (self.sigma**2)) 
        entryPriceAdjust = const * (entryPrice - self.mu)
        exitPriceAdjust  = const * (exitPrice - self.mu)
        
        return self.eta - self.ZV(entryPriceAdjust, exitPriceAdjust, self.costPrice, self.sigma)
    
    def Constraint2(self, x, costPrice, mu, theta, sigma):
        self.x          = x
        self.costPrice = costPrice
        self.mu         = mu
        self.theta      = theta
        self.sigma      = sigma
    
        entryPrice = self.x[0]
        exitPrice  = self.x[1]
        
        const = np.sqrt(2.0 * self.theta / (self.sigma**2)) 
        entryPriceAdjust = const * (entryPrice - self.mu)
        exitPriceAdjust  = const * (exitPrice - self.mu)
        costPriceAdjust  = const * self.costPrice
        
        #print(entryPriceAdjust, exitPriceAdjust, costPriceAdjust)
        # Ensure that entryPriceAdjust - exitPriceAdjust - costPriceAdjust >= 0
        return entryPriceAdjust - exitPriceAdjust - costPriceAdjust 

    def Constraint3(self, x, mu, theta, sigma):
        self.x     = x
        self.mu    = mu
        self.theta = theta
        self.sigma = sigma
        
        exitPrice = self.x[1]
        
        const = np.sqrt(2.0 * self.theta / (self.sigma**2)) 
        exitPriceAdjust  = const * (exitPrice - self.mu)
        
        return exitPriceAdjust #exitPrice > 0

    
    def w1(self, z, tolerance = 1e-8):
        self.z         = z
        self.tolerance = tolerance
        
        total1 = 0.0
        total2 = 0.0
        sqrt2z = np.sqrt(2) * self.z
        k = 1
        
        while True:
            term1 = (sqrt2z ** k) / factorial(k + 1) * gamma(k/2.0)
            term2 = (-sqrt2z ** k) / factorial(k + 1) * gamma(k/2.0)
            
            #Break the while loop when no longer adding material gain
            if abs(total1 - total2) <= tolerance:
                break
            
            total1 += term1
            total2 += term2
            
            k += 1
            
        total1 = (total1 * 0.5) ** 2
        total2 = (total2 * 0.5) ** 2
        
        return total1 - total2

    def w2(self, z, tolerance = 1e-8):
        self.z         = z
        self.tolerance = tolerance

        total = 0.0
        k = 1

        sqrt2z = np.sqrt(2) * self.z
        
        while True:
            const = 2 * k - 1
            constHalf = const / 2.0

            term = ((sqrt2z ** const) / factorial(const)) * gamma(constHalf) * digamma(constHalf)
            
            #Break the while loop when no longer adding material gain
            if abs(term) <= tolerance:
                break
            
            total += term
            k += 1
        
        return total
        
    def VarT(self, entryPrice, exitPrice):
        self.entryPrice = entryPrice
        self.exitPrice  = exitPrice
        
        return self.w1(self.entryPrice) - self.w1(self.exitPrice) - self.w2(self.entryPrice) + self.w2(self.exitPrice)
      
    def ET(self, entryPrice, exitPrice, tolerance = 1e-8):
        self.entryPrice = entryPrice
        self.exitPrice = exitPrice
        self.tolerance = tolerance
        
        sqrt2 = np.sqrt(2)
        total = 0.0
        k = 1
        
        while True:
            const = k * 2.0 - 1.0

            term = ((sqrt2 * self.entryPrice) ** const - (sqrt2 * self.exitPrice) ** const) / \
                        factorial(const + 1) * gamma(const / 2.0)
            
            if abs(term) < self.tolerance:
                break
            
            total += term
            k += 1
        
        return total
        
    def ZM(self, entryPrice, exitPrice, costPrice, mu, theta, sigma):
        self.entryPrice = entryPrice
        self.exitPrice  = exitPrice
        self.costPrice  = costPrice
        self.mu         = mu
        self.theta      = theta
        self.sigma      = sigma
        
        if self.ET(self.entryPrice, self.exitPrice) == 0:
            print(self.entryPrice, self.exitPrice, self.ET(self.entryPrice, self.exitPrice))
        
        ZMAdjust = np.sqrt(2 / (self.theta * self.sigma**2)) * \
                (self.exitPrice - self.entryPrice - self.costPrice) / self.ET(self.entryPrice, self.exitPrice)
                
        return ZMAdjust

    def ZV(self, entryPrice, exitPrice, costPrice, sigma):
        self.entryPrice = entryPrice
        self.exitPrice  = exitPrice
        self.costPrice  = costPrice
        self.sigma      = sigma

        pi = self.exitPrice - self.entryPrice - self.costPrice
        denom = self.ET(self.entryPrice, self.exitPrice)

        ZVAdjust = (2.0 / (self.sigma ** 2)) * (pi**2) * self.VarT(self.entryPrice, self.exitPrice)
                                                    
        return ZVAdjust