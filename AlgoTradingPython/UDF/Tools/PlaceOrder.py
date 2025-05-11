#Set directory
import os
os.chdir('/home/lun/Desktop/Folder 2/AlgoTradingPython')

from UDF.TWSWrapper import twsWrapper
from UDF.Contract   import MakeContract
from UDF.Orders     import Orders

#Library
import pandas as pd
import datetime as dt
import time as time

#======================================================================================
#**************************************************************************************
#TWS object
tws = twsWrapper.twsWrapper()

host = '127.0.0.1'
port = 7497
clientId = 3

#Login to TWS
tws.Login(host, port, clientId, 2)

#Market Data Type. 1 for live data, 4 for delayed data. 
marketDataType = 4

#======================================================================================
#**************************************************************************************
#Contract List
path = os.getcwd() + '/config/'
strategyName = 'MeanRevertingPortfolio'
optionStrat = 'option'
futures = 'futures'

#Create Contract
createContract = MakeContract.MakeContract()
contractDict = createContract.contractObjectList(path + strategyName + '.csv')
#**************************************************************************************
#======================================================================================

#======================================================================================
#**************************************************************************************
order = Orders.Orders(tws, 1)

#order.SingleMktOrder(contractDict['MSFT'], 'BUY', 20)
direction = ['BUY', 'BUY', 'BUY']
quantity  = [20, 30, 50]
order.MultiMktOrder(contractDict, direction, quantity)


#**************************************************************************************
#======================================================================================

