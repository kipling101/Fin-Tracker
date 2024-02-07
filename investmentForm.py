import yfinance as yf
import datetime; from datetime import timedelta, datetime
import mysql.connector
import pandas as pd
import tkinter as tk
from tkinter import *
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
        tk.messagebox.showerror(title="Add Investment", message="Error: Invalid Date.")
        return
    if addShareNum <= 0:
        tk.messagebox.showerror(title="Add Investment", message="Error: Invalid Number of Shares.")
        return
    if addStockTicker == "":
        tk.messagebox.showerror(title="Add Investment", message="Error: Invalid Stock Ticker.")
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
    
        #fetch all investments for the current holding from the SQL table
        cursor.execute("SELECT * FROM currInvestment WHERE stockTrnsID = %s", (i[4],))
        investments = cursor.fetchall()
        # Initialize the lists
        valHistory = []
        dateHistory = []

        # Iterate over each day
        for date, row in stockHist.iterrows():
            totalValue = 0

            # Iterate over each holding
            for i in curHolding:
                # Fetch all investments for the current holding from the SQL table
                cursor.execute("SELECT * FROM currinvestment WHERE stockTrnsID = %s AND shareDate <= %s", (i[4], date))
                investments = cursor.fetchall()

                # Iterate over each investment
                for investment in investments:
                    # Extract the number of shares and the opening price
                    sharesHeld = float(investment[2])  # replace 1 with the correct index for sharesHeld in your data
                    openPrice = stockHist['Open'][date]

                    # Calculate the value of this investment and add it to the total
                    totalValue += openPrice * sharesHeld

            # Append the total value and the date to the lists
            valHistory.append(totalValue)
            dateHistory.append(date.strftime('%Y-%m-%d'))

        print(valHistory, dateHistory)

        return [valHistory, dateHistory]

main = tk.Tk()
main.title("Investment")
main.geometry("500x500")  #sets the width and height 

#creates a graph of the investment value over time
f = Figure(figsize=(5,5), dpi=100)
a = f.add_subplot(111)

investmentOvTime = calcInvestment(userID, True)
#plots the investment value over time
a.plot(investmentOvTime[1], investmentOvTime[0], ls = '-')

a.set_title("Investment Value")
a.set_xlabel("Date")
a.set_ylabel("Value (£)")

canvas1=FigureCanvasTkAgg(f,master=main)
canvas1.draw()
canvas1.get_tk_widget().pack(side="top",fill='both',expand=True)


#creates the add cash function, with boxes
tk.Label(main, text="Add Cash", font='Helvetica 16').place(x=20, y=600)
#creates the add cash function, with boxes
addTicker = tk.Label(main, text="Name")
addTicker.place(x=50, y=640)
enterTickerName = Entry(main, width=35)
enterTickerName.place(x=75, y=670, width=100)

addStockAmount = tk.Label(main, text="Value")
addStockAmount.place(x=50, y=700)
enterStockAmount = Entry(main, width=35)
enterStockAmount.place(x=75, y=730, width=100)

addStockDate = tk.Label(main, text="Date")
addStockDate.place(x=50, y=760)
enterStockDate = Entry(main, width=35)
enterStockDate.place(x=75, y=790, width=100)

#button which adds the investment
addInvestButton = tk.Button(main, text="Add Cash", command=lambda: addInvestment(userID, enterTickerName.get(), enterStockAmount.get(), enterStockDate.get()))
addInvestButton.place(x=75, y=880, width=100)

tk.Label(main, text = "Remove Cash", font='Helvetica 16').place(x = 1000, y = 600)

#creates the remove cash function, with boxes
removeCashName = tk.Label(main, text="Name")
removeCashName.place(x=1000, y=640)
enterRemoveCashName = Entry(main, width=35)
enterRemoveCashName.place(x=1025, y=670, width=100)

removeCashAmount = tk.Label(main, text="Value")
removeCashAmount.place(x=1000, y=700)
enterRemoveCashAmount = Entry(main, width=35)
enterRemoveCashAmount.place(x=1025, y=730, width=100)

removeCashAPR = tk.Label(main, text="APR")
removeCashAPR.place(x=1000, y=780)
enterRemoveCashAPR = Entry(main, width=35)
enterRemoveCashAPR.place(x=1025, y=810, width=100)

#button which removes the cash
removeCashButton = tk.Button(main, text="Remove Cash", command=lambda: remInvestment(userID, enterRemoveCashName.get(), 
                                                                                  enterRemoveCashAmount.get(), enterRemoveCashAPR.get()))
removeCashButton.place(x=1000, y=840, width=100)

main.mainloop()