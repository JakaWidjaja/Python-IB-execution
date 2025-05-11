#Set directory
import os
os.chdir('/home/lun/Desktop/Folder 2/Strategy Development/Option Distributions')
directory = os.getcwd()

import pandas as pd
import datetime as dt
import math as math

from UDF.MonotoneHermiteCubic import MonotoneHermiteCubic

letters = ['F', 'G', 'H', 'J', 'K', 'M', 'N', 'Q', 'U', 'V', 'X', 'Z']
numbers = [2, 3, 4]

dates = []

#Get trading dates
for l in letters:
    for n in numbers:
        name = directory + '/data/CFE_VX_' + l + str(n) + '.csv'
        futuresData = pd.read_csv(name)
        futuresData['Trade Date'] = pd.to_datetime(futuresData['Trade Date'], format = '%Y-%m-%d').dt.date
        
        dates.extend(list(futuresData['Trade Date']))

dates = sorted(list(set(dates)), reverse = True)

futures = pd.DataFrame(columns = ['date'] + list(range(0, 121)))
futures['date'] = dates

#Create a dictionary for expiry dates
expiryDates = {'F2' : dt.datetime(2022, 1, 19).date(),  'F3' : dt.datetime(2023, 1, 18).date(),  'F4' : dt.datetime(2024, 1, 17).date(), 
               'G2' : dt.datetime(2022, 2, 16).date(),  'G3' : dt.datetime(2023, 2, 15).date(),  'G4' : dt.datetime(2024, 2, 14).date(),
               'H2' : dt.datetime(2022, 3, 15).date(),  'H3' : dt.datetime(2023, 3, 22).date(),  'H4' : dt.datetime(2024, 3, 20).date(),
               'J2' : dt.datetime(2022, 4, 20).date(),  'J3' : dt.datetime(2023, 4, 19).date(),  'J4' : dt.datetime(2024, 4, 17).date(),
               'K2' : dt.datetime(2022, 5, 18).date(),  'K3' : dt.datetime(2023, 5, 17).date(),  'K4' : dt.datetime(2024, 5, 22).date(),
               'M2' : dt.datetime(2022, 6, 15).date(),  'M3' : dt.datetime(2023, 6, 21).date(),  'M4' : dt.datetime(2024, 6, 18).date(),
               'N2' : dt.datetime(2022, 7, 20).date(),  'N3' : dt.datetime(2023, 7, 19).date(),  'N4' : dt.datetime(2024, 7, 17).date(),
               'Q2' : dt.datetime(2022, 8, 17).date(),  'Q3' : dt.datetime(2023, 8, 16).date(),  'Q4' : dt.datetime(2024, 8, 21).date(),
               'U2' : dt.datetime(2022, 9, 21).date(),  'U3' : dt.datetime(2023, 9, 20).date(),  'U4' : dt.datetime(2024, 9, 18).date(),
               'V2' : dt.datetime(2022, 10, 19).date(), 'V3' : dt.datetime(2023, 10, 18).date(), 'V4' : dt.datetime(2024, 10, 16).date(),
               'X2' : dt.datetime(2022, 11, 16).date(), 'X3' : dt.datetime(2023, 11, 15).date(), 'X4' : dt.datetime(2024, 11, 20).date(),
               'Z2' : dt.datetime(2022, 12, 21).date(), 'Z3' : dt.datetime(2023, 12, 20).date(), 'Z4' : dt.datetime(2024, 12, 18).date()}

#Import VIX index
vixIndex = pd.read_csv(directory + '/data/VIX Index.csv')
vixIndex['Date'] = pd.to_datetime(vixIndex['DATE'], format = '%m/%d/%Y').dt.date

for l in letters:
    for n in numbers:
        #Import futures data
        name = directory + '/data/CFE_VX_' + l + str(n) + '.csv'
        futuresData = pd.read_csv(name)
        futuresData['Trade Date'] = pd.to_datetime(futuresData['Trade Date'], format = '%Y-%m-%d').dt.date
        
        # Get the maximum date
        maxDate = expiryDates[l + str(n)]
        
        # Calculate the number of days difference
        futuresData['days'] = (maxDate - futuresData['Trade Date']).apply(lambda x: x.days)
        
        #input data per expiry day(s)
        for i in range(len(futuresData)):
            date = futuresData.iloc[i, 0]    
            numDays = futuresData.iloc[i, futuresData.columns.get_loc('days')]
            price = futuresData.iloc[i, futuresData.columns.get_loc('Settle')]

            if numDays > 120:
                continue
            futures.loc[futures['date'] == date, 0] = vixIndex.loc[vixIndex['Date'] == date, 'CLOSE'].values[0]
            futures.loc[futures['date'] == date, numDays] = price
            
cutOffDate = dt.datetime(2022,1,1).date()
futures = futures.loc[futures['date'] >= cutOffDate, :]

#interpolate 
expiryLimit = 60
for i in range(len(futures)):
    dataSeries = futures.iloc[i, 1:]
    dataSeries = dataSeries[~dataSeries.isnull()]
    
    expiry = list(dataSeries.index)
    prices = list(dataSeries.values)
    
    for k in range(1, expiryLimit + 1):
        if math.isnan(futures.iloc[i, futures.columns.get_loc(k)]):
            price = MonotoneHermiteCubic(k, expiry, prices).interpolate()
            futures.iloc[i, futures.columns.get_loc(k)] = price
                     
futures = futures.iloc[:, : (expiryLimit + 2)]

#send data to the data folder
futures.to_csv(directory + '/data/futures.csv', index = False)
