import numpy as np
from scipy.special import beta
import scipy.special as sc
from scipy.optimize import minimize

class BetaDistribution:
    def __init__(self):
        pass
    
    def OptionPrice(self, price, strike, expiry, rate, flag, a, b, p, q):
        self.price  = price
        self.strike = strike
        self.expiry = expiry
        self.rate   = rate
        self.flag   = flag
        self.a      = a
        self.b      = b
        self.p      = p
        self.q      = q
        
        # Discount factor
        discount = np.exp(-self.rate * self.expiry)
        
        # Avoid potential numerical instabilities with an epsilon
        epsilon = 1e-8
        ratio = (self.strike / (self.b * self.price)) ** self.a
        z = ratio / (1 + ratio + epsilon)
        
        # Correct order of arguments in hyp2f1
        lhs = 1 - (z ** (self.p + 1 / self.a)) / (sc.beta(self.p + 1 / self.a, self.q - 1 / self.a) * (self.p + 1 / self.a)) * \
              sc.hyp2f1(self.p + 1 / self.a, 1 + 1 / self.a, self.p + 1 / self.a + 1, z)

        rhs = 1 - (z ** self.p) / (sc.beta(self.p, self.q) * self.p) * \
              sc.hyp2f1(self.p, 1 - self.q, 1 + self.p, z)
            
        callValue = self.price * lhs - self.strike * discount * rhs
        
        if self.flag.lower() == 'put':
            return callValue - self.price + self.strike * discount
        else:
            return callValue
        
    def u(self, i, a, b, p, q):
        self.i = i
        self.a = a
        self.b = b
        self.p = p
        self.q = q
        
        value = self.b ** self.i * beta(self.p + self.i / self.a, self.q - self.i / self.a) / beta(self.p, self.q)
        
        return value
    
    def Moment(self, i, a, b, p, q):
        self.i = i
        self.a = a
        self.b = b
        self.p = p
        self.q = q
        
        if i >= 1:
            index1 = self.u(1, self.a, self.b, self.p, self.q)
        if i >= 2:
            index2 = self.u(2, self.a, self.b, self.p, self.q)
        if i >= 3:
            index3 = self.u(3, self.a, self.b, self.p, self.q)
        if i >= 4:
            index4 = self.u(4, self.a, self.b, self.p, self.q)
        
        if i == 1:
            return index1
        elif i == 2:
            return index2 - index1**2
        elif i == 3:
            return (index3 - 3 * index1 * index2 + 2 * index1**3) / ((index2 - index1**2)**(3/2))
        elif i == 4:
            return (index4 - 4*index1*index3 + 6*index2*index1**2 - 3*index1**4) / ((index2 - index1**2)**2)
        
    def calibrate(self, price, strike, expiry, rate, flag, target_price):
        # Initial guesses for a, b, p, and q
        initial_guess = [1.0, 1.0, 2.0, 2.0]  # Starting guesses for a, b, p, q

        # Objective function to minimize the difference between the calculated and target option price
        def objective(params):
            a, b, p, q = params
            # Ensure p and q are positive
            if p <= 0 or q <= 0 or b <= 0:
                return np.inf
            calculated_price = self.OptionPrice(price, strike, expiry, rate, flag, a, b, p, q)
            return (calculated_price - target_price) ** 2
        
        # Using minimize from scipy to find the best fit for a, b, p, and q
        result = minimize(objective, initial_guess, bounds=[(0.1, 10), (0.1, 10), (0.1, 10), (0.1, 10)])

        if result.success:
            a, b, p, q = result.x
            return a, b, p, q
        else:
            raise ValueError("Calibration failed")
            
            
if __name__ == '__main__':
    opt = BetaDistribution()

    expiry = 20/365
    rate = 0.0549
    strike = 15
    price = 20.8277
    flag = 'Call'
    targetPrice = 5.95
    
    a, b, p, q = opt.calibrate(price, strike, expiry, rate, flag, targetPrice)
    
    opt.OptionPrice(price, strike, expiry, rate, flag, a, b, p, q)

    opt.Moment(1, a, b, p, q)
    opt.Moment(2, a, b, p, q)
    opt.Moment(3, a, b, p, q)
    opt.Moment(4, a, b, p, q)
    
    from scipy.optimize import minimize
    
    def objective(params, opt, target_moment):
        a, b, p, q = params
        moment_value = opt.Moment(2, a, b, p, q)
        return abs(moment_value - target_moment)
    
    target_moment = 0.2
    init = [0.924, 1.187, 21.84, 26.08]
    
    result = minimize(objective, init, args=(opt, target_moment), method='SLSQP')
    a = result.x[0]
    b = result.x[1]
    p = result.x[2]
    q = result.x[3]