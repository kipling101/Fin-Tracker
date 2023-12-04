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
#must verify date is in correct format
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
        stockInfo = yf.Ticker(stockTicker)
        stockHist = stockInfo.history(start=datePur, end=currentDate, interval = '1d')
        closingFirst = stockHist['Open'][0]
        closingCurr = stockHist['Open'][len(stockHist)-1]
        currPrice = round(closingCurr*float(sharesHeld),5)
        origPrice = round(closingFirst*float(sharesHeld),5)
        print("Stock ticker: ", stockTicker, "has current value", currPrice, "and initial value", origPrice)

calcInvestment(userID)


