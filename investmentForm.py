import numpy as np 
import pandas as pd
import yfinance as yf
from statistics import mean
import datetime; from datetime import timedelta, datetime
import mysql.connector
from mysql.connector import Error

userID = 1
stockTicker = 'AAPL'
numSharesHeld = 43.0
shareDate = '2020-01-03'

remStockTicker = 'AAPL'
remNumSharesHeld = 43.0
remShareDate = '2020-01-03'

def addInvestment(userID, stockTicker, numSharesHeld, shareDate):

    db = mysql.connector.connect(host ="localhost", user = "root", password = "pass123", db ="FinTracker")
    cursor = db.cursor()

    addInvSQL = "INSERT INTO currInvestment (userID, stockTicker, numSharesHeld, shareDate) VALUES (%s, %s, %s, %s)"
    cursor.execute(addInvSQL, (userID, stockTicker, numSharesHeld, shareDate))
    db.commit()

    print("Investment added successfully!")

def remInvestment(userID, remStockTicker, remNumSharesHeld, remShareDate):

    db = mysql.connector.connect(host ="localhost", user = "root", password = "pass123", db ="FinTracker")
    cursor = db.cursor()

    remInvSQL = "SELECT * FROM currInvestment WHERE userID = %s AND stockTicker = %s AND numSharesHeld = %s AND shareDate = %s"
    cursor.execute(remInvSQL, (userID, remStockTicker, remNumSharesHeld, remShareDate))
    results = cursor.fetchall()

    #can be improved by using transaction ID instead of searching against all fields
    if results:
        removeInvSQL = "DELETE FROM currInvestment WHERE userID = %s AND stockTicker = %s AND numSharesHeld = %s AND shareDate = %s"
        cursor.execute(removeInvSQL, (userID, remStockTicker, remNumSharesHeld, remShareDate))
        db.commit()
        print("Investment removed successfully!")

    else:    
        print("No such investment exists, please verify data inputted and try again.")


def calcInvestment(userID):
    db = mysql.connector.connect(host ="localhost", user = "root", password = "pass123", db ="FinTracker")
    cursor = db.cursor()

    calcInvSQL = "SELECT * FROM currInvestment WHERE userID = %s"
    cursor.execute(calcInvSQL, (userID,))
    curHolding = cursor.fetchall()

    for i in curHolding:

        stockTicker = i[1]
        sharesHeld = i[2]
        datePur = i[3]

        currentDate = datetime.now().strftime('%Y-%m-%d')
        date = datetime.strptime(datePur, '%Y-%m-%d')
        stockInfo = yf.Ticker(stockTicker)
        stockHist = stockInfo.history(start=datePur, end=currentDate, interval = '1d')
        print(stockHist)

       #extract the relevant information from the stockHist dataframe
        #to do: find initial price, find final price, find difference, find percentage change

addInvestment(userID, stockTicker, numSharesHeld, shareDate)
calcInvestment(userID)


