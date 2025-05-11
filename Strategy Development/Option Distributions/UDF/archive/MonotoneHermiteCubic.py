import numpy as np

class MonotoneHermiteCubic(object):
    def __init__(self,x, xArray, yArray):
        self.x       = x
        self.xArray = np.array(xArray)
        self.yArray = np.array(yArray)

    def interpolate(self):
        #Check if the value already exist. If there is, then no need to interpolate
        if self.x in self.xArray:
            index = np.where(self.xArray == self.x)
            return self.yArray[index[0][0]]
        
        #Calculate the slope of the secant lines between successive points. 
        delta = (self.yArray[1:] - self.yArray[0:-1]) / (self.xArray[1:] - self.xArray[0:-1])

        #Initialised the tangents at every data points. 
        m = [(delta[i - 1] + delta[i])/2.0 if np.sign(delta[i-1]) == np.sign(delta[i]) else 0.0 
             for i in range(1, (len(self.yArray)-1))]

        #Condition for each endpoints. 
        m.insert(0,0)
        m.insert(len(m), delta[-1])
        
        #Check if consecutive points are flat. Then set m = 0
        for i in range(0, len(delta)-1):
            if delta[i] == 0:
                m[i] = 0
                m[i+1] = 0
            else:
                #Check for monotonicity. 
                alpha = 0.0
                beta = 0.0
                tau = 0.0
                for i in range(0, len(delta)-1):
                    alpha = m[i] / delta[i]
                    beta = m[i+1] / delta[i]
                    tau = 3 / np.sqrt(alpha**2 + beta**2)
                    #This part below ensure monotonicity. 
                    if (alpha**2 + beta**2) > 9:
                        m[i] = tau * alpha * delta[i]
                        m[i+1] = tau * beta * delta[i]
        
        #This section performs the Cubic Hermite Spline interpolation.      
        #Find the upper and lower existing values. 
        
        for i in range(0, len(self.xArray)-1):
            if self.x > self.xArray[i] and self.x < self.xArray[i+1]:
                xUpper = self.xArray[i+1]
                xLower = self.xArray[i]
                yUpper = self.yArray[i+1]
                yLower = self.yArray[i]
                mUpper = m[i+1]
                mLower = m[i]
                
        h = xUpper - xLower
        t = (self.x - xLower) / h

        #Expanded
        h00 = 2 * (t**3) - 3 * (t**2) + 1
        h10 = (t**3) - 2 * (t**2) + t
        h01 = -2 * (t**3) + 3 * (t**2)
        h11 = (t**3) - (t**2)
        
        '''
        #Factorised
        h00 = (1 + 2*t) * ((1 - t)**2)
        h10 = t * ((1-t)**2)
        h01 = (t**2) * (3 - 2 * t)
        h11 = (t**2) *(t-1) 
        '''
        
        '''
        #Bernstein
        B0 = (1 - t) ** 3
        B1 = 3 * t * (1-t)**2
        B2 = 3 * (t**2) * (1 - t)
        B3 = t**3
        
        h00 = B0 + B1
        h10 = (1/3) * B1
        h01 = B3 + B2
        h11 = (-1/3) * B2
        '''     
        
        interpolatedValue = (yLower * h00) + (h * mLower * h10) + (yUpper * h01) + (h * mUpper * h11)
        
        return interpolatedValue 
    
if __name__ == '__main__':
    expiry = [0.0,   26.0,   54.0,   82.0,   117.0,  145.0,  173.0]
    future = [11.47, 13.325, 15.250, 16.075, 16.675, 17.275, 17.525]
    
    interp = MonotoneHermiteCubic(75.0, expiry, future)
    interp.interpolate()
    
    #expiry[1:] - expiry[0:-1]
