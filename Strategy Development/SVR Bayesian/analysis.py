#Set directory
import os
os.chdir('/home/lun/Desktop/Folder 2/Strategy Development/SVR Bayesian')
directory = os.getcwd()

import pandas   as pd
import numpy    as np
import datetime as dt
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

from UDF.SVR import SVRBayesian

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
timeSeries = list(pricesDate2['close'])

SVRModel = SVRBayesian.SVRBayesian()

# Create lagged features
def create_lagged_features(data, lag=5):
    X, y = [], []
    for i in range(len(data) - lag):
        X.append(data[i:i+lag])
        y.append(data[i+lag])
    return np.array(X), np.array(y)

lag = 30
X, y = create_lagged_features(timeSeries, lag)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.7, shuffle=False)

SVRModel.Fit(X_train, y_train)

y_pred = SVRModel.predict(X_test)

plt.figure(figsize=(8, 6))
plt.plot(y_test, label="Actual", marker="o")
plt.plot(y_pred, label="Predicted", marker="x")
plt.xlabel("Sample Index")
plt.ylabel("Value")
plt.title("Actual vs Predicted Values")
plt.legend()
plt.show()
#**************************************************************************************
#======================================================================================











































