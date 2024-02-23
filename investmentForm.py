import yfinance as yf
import datetime; from datetime import timedelta, datetime
import mysql.connector
import pandas as pd
import tkinter as tk
from tkinter import *; from tkinter import ttk
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

def openInvestmentForm(userID):
    
    db = mysql.connector.connect(host ="localhost", user = "root", password = "pass123", db ="FinTracker")
    cursor = db.cursor()

    def addInvestment(userID, addStockTicker, addShareNum, addShareDate):

        if addShareDate > datetime.now().strftime('%Y-%m-%d') or addShareDate == "":
            tk.messagebox.showerror(title="Add Investment", message="Error: Invalid Date.")
            return
        if float(addShareNum) <= 0:
            tk.messagebox.showerror(title="Add Investment", message="Error: Invalid Number of Shares.")
            return
        if addStockTicker == "":
            tk.messagebox.showerror(title="Add Investment", message="Error: Invalid Stock Ticker.")
            return
        #inserts the inputted data into the currInvestment table
        addInvSQL = "INSERT INTO currInvestment (userID, stockTicker, numSharesHeld, shareDate) VALUES (%s, %s, %s, %s)"
        cursor.execute(addInvSQL, (userID, addStockTicker, addShareNum, addShareDate))
        db.commit()

        tk.messagebox.showinfo("Success", "Investment added successfully!")

    def remInvestment(userID, remStockTicker, remShareNum):

        #checks if there is a investment that matches the inputted data
        remInvSQL = "SELECT * FROM currInvestment WHERE userID = %s AND stockTicker = %s"
        cursor.execute(remInvSQL, (userID, remStockTicker,))
        results = cursor.fetchall()

        #if a result is returned, deletes the investment from the database
        if results and results[2] >= remShareNum:
            newShareNum = remShareNum * -1
            
            removeInvSQL = "INSERT INTO currInvestment (userID, stockTicker, numSharesHeld, shareDate) VALUES (%s, %s, %s, %s)"
            cursor.execute(removeInvSQL, (userID, remStockTicker, float(newShareNum), datetime.now().strftime('%Y-%m-%d'),))
            db.commit()

            tk.messagebox.showinfo("Success", "Investment removed successfully!")
        else:    
            tk.messagebox.showerror("Error", "Investment not found!")

    def calcInvestment(userID):

        #finds all of the investment information for the user given by the userID
        calcInvSQL = "SELECT * FROM currInvestment WHERE userID = %s"
        cursor.execute(calcInvSQL, (userID,))
        curHolding = cursor.fetchall() #returns all the rows

        for i in curHolding:
            #for each investment, finds the current price and the initial price
            stockTicker = i[1]
            sharesHeld = i[2]
            datePur = i[3]
            
            currentDate = datetime.now().strftime('%Y-%m-%d') #finds the current date
            stockInfo = yf.Ticker(stockTicker) #sets the ticket to a given variable
            #finds the daily stock history information from the date of purchase to the current date
            stockHist = stockInfo.history(start=datePur, end=currentDate, interval = '1d')
        
            #fetch all investments for the current holding from the SQL table
            cursor.execute("SELECT * FROM currInvestment WHERE stockTrnsID = %s", (i[4],))
            investments = cursor.fetchall()
            
            valHistory = []
            dateHistory = []

            #iterate over each day
            for date, row in stockHist.iterrows():
                totalValue = 0

                #iterate over each holding
                for i in curHolding:
                    #fetch all investments for the current holding from the SQL table
                    cursor.execute("SELECT * FROM currinvestment WHERE stockTrnsID = %s AND shareDate <= %s", (i[4], date))
                    investments = cursor.fetchall()

                    #iterate over each investment
                    for investment in investments:
                        # Extract the number of shares and the opening price
                        sharesHeld = float(investment[2])  # replace 1 with the correct index for sharesHeld in your data
                        openPrice = stockHist['Open'][date]

                        #calculate teh value of this investment and add it to the total
                        totalValue += openPrice * sharesHeld

                #append the total value and the date to the lists
                valHistory.append(totalValue)
                dateHistory.append(date.strftime('%Y-%m-%d'))

            return [valHistory, dateHistory]

    main = tk.Tk()
    main.title("Cash")
    main.geometry("500x500")  # Set your desired width and height

    width, height = 300, 300

    #converts from px to inches
    figsize = (3, 3)

    #creates the window for the graph of a set size
    f = Figure(figsize=figsize, dpi=100)
    #adds a subplot to the window
    a = f.add_subplot(111)

    #plots the data on the graph
    investOverTime = calcInvestment(userID)
    a.plot(investOverTime[1], investOverTime[0], ls='-')
    a.set_title("Value")
    a.set_xlabel("Date")

    #creates the canvas for the graph to be displayed on
    canvas = FigureCanvasTkAgg(f, master=main)
    canvas.draw()
    canvas.get_tk_widget().pack()

    #creates the add cash function, with boxes
    tk.Label(main, text="Add Investment", font='Helvetica 16').place(x=20, y=600)
    #creates the add cash function, with boxes
    addTicker = tk.Label(main, text="Ticker")
    addTicker.place(x=50, y=640)
    enterTickerName = Entry(main, width=35)
    enterTickerName.place(x=75, y=670, width=100)

    addStockAmount = tk.Label(main, text="Quantity to Add")
    addStockAmount.place(x=50, y=700)
    enterStockAmount = Entry(main, width=35)
    enterStockAmount.place(x=75, y=730, width=100)

    addStockDate = tk.Label(main, text="Date")
    addStockDate.place(x=50, y=760)
    enterStockDate = Entry(main, width=35)
    enterStockDate.place(x=75, y=790, width=100)

    #button which adds the investment
    addInvestButton = tk.Button(main, text="Add Investment", command=lambda: addInvestment(userID, enterTickerName.get(), enterStockAmount.get(), 
                                                                                        enterStockDate.get()))
    addInvestButton.place(x=75, y=880, width=100)

    tk.Label(main, text = "Liquidate Position", font='Helvetica 16').place(x = 1000, y = 600)

    #creates the remove cash function, with boxes
    removeStockQuan = tk.Label(main, text="Quantity to Remove")
    removeStockQuan.place(x=1000, y=700)
    enterRemoveStockQuan = Entry(main, width=35)
    enterRemoveStockQuan.place(x=1025, y=730, width=100)

    cursor.execute("SELECT * FROM currInvestment WHERE userID = %s", (userID,))
    curInvestment = cursor.fetchall()

    #creates a dropdown box which contains the tranaction ids for the debts
    investCombobox = ttk.Combobox(main, values=[investment[1] for investment in curInvestment])
    investCombobox.place(x=1025, y=650, width=100)
    #button which removes the debt
    removeDebtButton = tk.Button(main, text="Liquidate Position", command=lambda: remInvestment(userID, investCombobox.get(), 
                                                                                                float(enterRemoveStockQuan.get()))).place(x=1000, y=780, width=100)

    main.mainloop()