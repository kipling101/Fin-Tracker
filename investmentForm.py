import yfinance as yf
import datetime; from datetime import timedelta, datetime
import mysql.connector

userID = 1
addStockTicker = 'AAPL'
addShareNum = 43.0
addShareDate = '2020-01-03'
#must verify date is in correct format
remStockTicker = 'AAPL'
remShareNum = 43.0


def addInvestment(userID, addStockTicker, addShareNum, addShareDate):
    #initialise database connection
    db = mysql.connector.connect(host ="localhost", user = "root", password = "pass123", db ="FinTracker")
    cursor = db.cursor()
    #inserts the inputted data into the currInvestment table
    addInvSQL = "INSERT INTO currInvestment (userID, stockTicker, numSharesHeld, shareDate) VALUES (%s, %s, %s, %s)"
    cursor.execute(addInvSQL, (userID, addStockTicker, addShareNum, addShareDate))
    db.commit()

    print("Investment added successfully!")

def remInvestment(userID, remStockTicker, remShareNum, remShareDate):
    #initialise database connection
    db = mysql.connector.connect(host ="localhost", user = "root", password = "pass123", db ="FinTracker")
    cursor = db.cursor()
    #checks if there is a investment that matches the inputted data
    remInvSQL = "SELECT * FROM currInvestment WHERE userID = %s AND stockTicker = %s AND numSharesHeld = %s"
    cursor.execute(remInvSQL, (userID, remStockTicker, remShareNum,))
    results = cursor.fetchall()

    #if a result is returned, deletes the investment from the database !! CHANGE VARIABLE NAME !!
    if results:
        removeInvSQL = "DELETE FROM currInvestment WHERE userID = %s AND stockTicker = %s AND numSharesHeld = %s AND shareDate = %s"
        cursor.execute(removeInvSQL, (userID, remStockTicker, remShareNum, remShareDate))
        db.commit()

        print("Investment removed successfully!")

    else:    
        print("No such investment exists, please verify data inputted and try again.")

def calcInvestment(userID):
    #initialise database connection
    db = mysql.connector.connect(host ="localhost", user = "root", password = "pass123", db ="FinTracker")
    cursor = db.cursor()
    #finds all of the investment information for the user given by the userID
    calcInvSQL = "SELECT * FROM currInvestment WHERE userID = %s"
    cursor.execute(calcInvSQL, (userID,))
    curHolding = cursor.fetchall() #returns all the rows as a list of tuples

    for i in curHolding:
        #for each investment, finds the current price and the initial price
        stockTicker = i[1]
        sharesHeld = i[2]
        datePur = i[3]
        
        currentDate = datetime.now().strftime('%Y-%m-%d') #finds the current date
        stockInfo = yf.Ticker(stockTicker) #sets the ticket to a given variable
        #finds the daily stock history information from the date of purchase to the current date
        stockHist = stockInfo.history(start=datePur, end=currentDate, interval = '1d')
        closingFirst = stockHist['Open'][0] #finds the opening price on the date of purchase
        closingCurr = stockHist['Open'][len(stockHist)-1] #finds the opening price on the current date, use closing price?
        currPrice = round(closingCurr*float(sharesHeld),5) #calculates the current price of the investment
        origPrice = round(closingFirst*float(sharesHeld),5) #calculates the initial price of the investment
        print("Stock ticker: ", stockTicker, "has current value", currPrice, "and initial value", origPrice)

calcInvestment(userID)


