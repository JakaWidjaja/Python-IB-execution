#Set directory
import os
os.chdir('/home/lun/Desktop/Folder 2/Strategy Development/Stock Price HMM')
directory = os.getcwd()

import pandas   as pd
import numpy    as np
import datetime as dt
import matplotlib.pyplot as plt


from UDF.HMM import HMM

#======================================================================================
#**************************************************************************************
#import data
#1-Day tick option
tickData              = pd.read_csv(directory + '/data/AAPL.csv')
tickData['date']      = pd.to_datetime(tickData['date'], format = '%Y%m%d %H:%M:%S')
tickData['date just'] = pd.to_datetime(tickData['date'], format = '%Y%m%d %H:%M:%S').dt.date
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
#Available dates
dates = sorted(list(set(tickData['date just'])))

#date1 < date2 < ... < date(n)
date1Start = dt.datetime(2024, 10, 3, 23, 0, 0)
date1End   = dt.datetime(2024, 10, 4, 6 , 0, 0)

date2Start = dt.datetime(2024, 10, 4, 23, 0, 0)
date2End   = dt.datetime(2024, 10, 5, 6 , 0, 0)

date3Start = dt.datetime(2024, 10, 8, 0, 30, 0)
date3End   = dt.datetime(2024, 10, 8, 7, 0 , 0)

date4Start = dt.datetime(2024, 10, 9, 0, 30, 0)
date4End   = dt.datetime(2024, 10, 9, 7, 0 , 0)

date5Start = dt.datetime(2024, 10, 10, 0, 30, 0)
date5End   = dt.datetime(2024, 10, 10, 7, 0 , 0)
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
pricesDate1 = tickData.loc[(tickData['date'] >= date1Start) & (tickData['date'] <= date1End), ['date', 'close']]
pricesDate2 = tickData.loc[(tickData['date'] >= date2Start) & (tickData['date'] <= date2End), ['date', 'close']]
pricesDate3 = tickData.loc[(tickData['date'] >= date3Start) & (tickData['date'] <= date3End), ['date', 'close']]
pricesDate4 = tickData.loc[(tickData['date'] >= date4Start) & (tickData['date'] <= date4End), ['date', 'close']]
pricesDate5 = tickData.loc[(tickData['date'] >= date5Start) & (tickData['date'] <= date5End), ['date', 'close']]
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
modelHMM = HMM.HMM(numStates = 2)

data = pricesDate1

#calibration
numCalibrationData = 100
calibData = np.array(data[:numCalibrationData]['close'])

#Apply Kalman Filter smoothing


modelHMM.Fit(calibData)

# Predict hidden states
hiddenStates = modelHMM.PredictStates()

#Simulated Prices
numSimulation = 30
simulatedPrices = modelHMM.SimulatePrice(calibData[-1], numSimulation)

simDataActual = np.array(data[numCalibrationData : (numCalibrationData + numSimulation)]['close'])

plt.plot(simDataActual, label = 'Actual')
plt.plot(simulatedPrices, label = 'Simulated')
plt.legend()
#**************************************************************************************
#======================================================================================
plt.plot(calibData)

plt.plot(np.array(pricesDate1['close']))


















































