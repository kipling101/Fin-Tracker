import yfinance as yf
import datetime; from datetime import timedelta, datetime
import mysql.connector
import pandas as pd
import tkinter as tk
from tkinter import messagebox
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

userID = 1
addStockTicker = 'AAPL'
addShareNum = 43.0
addShareDate = '2023-12-08'
#must verify date is in correct format
remStockTicker = 'AAPL'
remShareNum = 43.0

db = mysql.connector.connect(host ="localhost", user = "root", password = "pass123", db ="FinTracker")
cursor = db.cursor()

def addInvestment(userID, addStockTicker, addShareNum, addShareDate):

    if addShareDate > datetime.now().strftime('%Y-%m-%d') or addShareDate == "":
        tk.m
        return
    if addShareNum <= 0:
        print("Error: Number of shares must be greater than 0.")
        return
    if addStockTicker == "":
        print("Error: Stock ticker cannot be empty.")
        return
    #inserts the inputted data into the currInvestment table
    addInvSQL = "INSERT INTO currInvestment (userID, stockTicker, numSharesHeld, shareDate) VALUES (%s, %s, %s, %s)"
    cursor.execute(addInvSQL, (userID, addStockTicker, addShareNum, addShareDate))
    db.commit()

    print("Investment added successfully!")

def remInvestment(userID, remStockTicker, remShareNum, remShareDate):

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

def calcInvestment(userID, totalCheck):
    valHistory = []; dateHistory = []; runningTotal = 0
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
        closingCurr = stockHist['Open'][len(stockHist)-1] #finds the opening price on the current date
        currPrice = round(closingCurr*float(sharesHeld),5) #calculates the current price of the investment
        origPrice = round(closingFirst*float(sharesHeld),5) #calculates the initial price of the investment
        print("Stock ticker: ", stockTicker, "has current value", currPrice, "and initial value", origPrice)

        if totalCheck == True:
            for date, row in stockHist.iterrows():

                valHistory.append(stockHist['Open'][date]*float(sharesHeld))
                dateHistory.append(date.strftime('%Y-%m-%d'))
            
            return [valHistory, dateHistory]

main = tk.Tk()
main.title("Modify Permissions")
main.geometry("500x500")  #sets the width and height 

#creates a graph of the investment value over time
f = Figure(figsize=(5,5), dpi=100)
a = f.add_subplot(111)

a.plot(calcInvestment(userID, True)[1], calcInvestment(userID, True)[0], ls = '-')

a.set_title("Investment Value")
a.set_xlabel("Date")
a.set_ylabel("Value (£)")

canvas1=FigureCanvasTkAgg(f,master=main)
canvas1.draw()
canvas1.get_tk_widget().pack(side="top",fill='both',expand=True)

main.mainloop()