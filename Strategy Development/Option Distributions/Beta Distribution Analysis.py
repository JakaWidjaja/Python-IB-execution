#Set directory
import os
os.chdir('/home/lun/Desktop/Folder 2/Strategy Development/Option Distributions')
directory = os.getcwd()

import scipy.special as sc
from scipy.optimize import minimize, differential_evolution
from scipy.integrate import quad
from scipy.special import beta
import numpy as np
import pandas as pd

def optionBeta(price, strike, expiry, rate, flag, a, b, p, q):
    z = (1 + (strike / b)**-a)**-1
    
    discount = np.exp(-rate * expiry)
    
    if flag == 'Call' or flag == 'call':
        betaCDF1 = sc.betainc(p + 1/a, q - 1/a, z)
        betaCDF2 = sc.betainc(p, q, z)
        value = discount * (price * (1 - betaCDF1) - strike * (1 - betaCDF2))
        
    return value

expiry = 20/365
price = 20.66
strike = [15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
strike = [20]
rate = 0.0549
flag = 'Call'

a = 0.5
b = 0.5
p = 3.8
q = 3.2

optionMarketPrice = [5.94999980926514,
5.15000057220459,
4.19999980926514,
3.05000019073486,
2.35999965667725,
1.80000019073486,
1.47000026702881,
1.23000049591064,
1.02999973297119,
0.889999985694885,
0.759999990463257,
0.660000026226044,
0.569999992847443,
0.509999990463257,
0.439999997615814
]
optionMarketPrice = [1.80000019073486]

def errorFunc(params, price, strike, expiry, rate, flag, marketPrice):
    a, b, p, q = params
    totalError = 0
    for i in range(len(strike)):
        modelPrice = optionBeta(price, strike[i], expiry, rate, flag, a, b, p, q)
        totalError += (modelPrice - marketPrice[i]) ** 2
    return totalError

initGuess = [0.5, 0.5, 3.8, 3.2]
result = minimize(errorFunc, initGuess, args = (price, strike, expiry, rate, flag, optionMarketPrice), 
                  method = 'SLSQP')

param = result.x
a = param[0]
b = param[1]
p = param[2]
q = param[3]

optionBeta(price, strike[0], expiry, rate, flag, a, b, p, q)

#Variance==============================================================================
limit = (1 + (strike[0] / b)**-a)**-1

def incomplete_beta_second_kind(x, a, b):
    integrand = lambda t: (t**(a-1)) / ((1+t)**(a+b))
    result, _ = quad(integrand, 0, x)
    return result

def calculate_variance_incomplete_beta(a, b, x, num_samples=10000):
    samples = []
    
    for _ in range(num_samples):
        # Simulate a random sample from the distribution
        # Note: This is a simplified approach; accurate sampling may require more sophisticated techniques
        z = np.random.uniform(0, x)
        sample_value = incomplete_beta_second_kind(z, a, b)
        samples.append(sample_value)
    
    samples = np.array(samples)
    
    # Calculate mean and variance
    mean_value = np.mean(samples)
    variance = np.var(samples, ddof=1)  # Using ddof=1 for sample variance
    
    return mean_value, variance

ave, var = calculate_variance_incomplete_beta(a, b, limit)
sigma = np.sqrt(var)

#==============================================================================
#calibrate the beta distribution from time series

futuresData = pd.read_csv(directory + '/data/futures.csv')
dailyReturn = futuresData.copy()
dailyReturn.iloc[:, 1:] = dailyReturn.iloc[:, 1:].pct_change()
dailyReturn = dailyReturn.dropna()

numReturns = 250
expiryDay = 20
dataToUse = dailyReturn.iloc[0:, dailyReturn.columns.get_loc(str(expiryDay))]
dataToUse = dataToUse[dataToUse > 0] 

def gb2_pdf(x, a, b, p, q):
    # Generalized Beta distribution of the second kind
    return (a * (x**(a*p - 1))) / (b**(a*p) * beta(p, q) * (1 + (x/b)**a)**(p+q))

def neg_log_likelihood(params, data):
    a, b, p, q = params
    likelihoods = gb2_pdf(data, a, b, p, q)
    return -np.sum(np.log(likelihoods))

guess = [1.33392196, 2.42105098, 4.01530805, 2.22135524]
bnd = [(0.1, np.inf), (0.1, np.inf), (0.1, np.inf), (0.1, np.inf)]
bnd = [(-np.inf, np.inf), (-np.inf, np.inf), (-np.inf, np.inf), (-np.inf, np.inf)]
result = minimize(neg_log_likelihood, guess, args=(dataToUse,), method='L-BFGS-B', bounds = bnd)
result = differential_evolution(neg_log_likelihood, bounds=bnd, args=(dataToUse,))

a = result.x[0]
b = result.x[1]
p = result.x[2]
q = result.x[3]
optionBeta(price, 20, expiry, rate, flag, a, b, p, q)
