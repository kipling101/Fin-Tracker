import yfinance as yf
import datetime; from datetime import timedelta, datetime
import mysql.connector
import tkinter as tk; from tkinter import messagebox; from tkinter import Entry; from tkinter import ttk; from tkinter import tix; from tkinter.tix import Balloon
import matplotlib; matplotlib.use('TkAgg'); from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg; from matplotlib.figure import Figure
import menu

db = mysql.connector.connect(host ="localhost", user = "root", password = "pass123", db ="FinTracker")
cursor = db.cursor()

def openInvestmentForm(userID):
    
    def addInvestment(userID, addStockTicker, addShareNum, addShareDate):
        try:
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
        except mysql.connector.errors.DataError:
            tk.messagebox.showerror(title="Add Cash", message="Error: Entry Data.")
        except Exception as e:
            tk.messagebox.showerror(title="Add Cash", message="Error: " + str(e))


    def remInvestment(userID, remStockTicker, remShareNum):
        try:
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
        except mysql.connector.errors.DataError:
            tk.messagebox.showerror(title="Error",message="Invalid data entered.")
        except Exception as e: 
            tk.messagebox.showerror(title="Error", message="Error: " + str(e))

    def calcInvestment(userID):
        try:
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
                            
                            sharesHeld = float(investment[2]) 
                            #calculate teh value of this investment and add it to the total
                            totalValue += stockHist['Open'][date] * sharesHeld

                    #append the total value and the date to the lists
                    valHistory.append(totalValue)
                    dateHistory.append(date.strftime('%Y-%m-%d'))

                return [valHistory, dateHistory]
        except mysql.connector.errors.DataError:
            tk.messagebox.showerror(title="Error",message="Invalid data entered.")
        except Exception as e: 
            tk.messagebox.showerror(title="Error", message="Error: " + str(e))
    try:
        main = tix.Tk()
        main.title("Investment")
        main.state('zoomed') #sets the desired width and height of the image
        #creates the menu
        menu.createMenu(main, userID)
        width, height = 300, 300

        #converts from px to inches
        figsize = 5.5,4

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

        #creates the information table
        breakLabel = tk.Label(main, text = "", font='Helvetica 16').pack() #creates a gap for aesthetics
        tree = ttk.Treeview(main)
        columns = ('Name', 'Amount', 'Date', 'APR', 'Transaction Number')  #column names

        #create columns
        tree['columns'] = columns

        for column in columns:
            tree.heading(column, text=column)
            tree.column(column, width=60)

        #adds only rows 1,2,4,5 to the table
        for i, row in enumerate(curInvestment):
            tree.insert('', 'end', values=(row[1], row[2], row[3], row[4], row[5]))
        tree.column('#0', width=0)  #makes the first column v. small
        #adds the table to the window
        tree.pack()

        #creates the add investment function, with boxes
        tk.Label(main, text="Add Investment", font='Helvetica 16').place(x=430, y=600)
    
        addTicker = tk.Label(main, text="Ticker")
        addTicker.place(x=445, y=640)
        enterTickerName = Entry(main, width=35)
        enterTickerName.place(x=470, y=670, width=100)

        addStockAmount = tk.Label(main, text="Quantity to Add")
        addStockAmount.place(x=445, y=700)
        enterStockAmount = Entry(main, width=35)
        enterStockAmount.place(x=470, y=730, width=100)

        addStockDate = tk.Label(main, text="Date")
        addStockDate.place(x=445, y=760)
        enterStockDate = Entry(main, width=35)
        enterStockDate.place(x=470, y=790, width=100)

        #button which adds the investment
        addInvestButton = tk.Button(main, text="Add Investment", command=lambda: addInvestment(userID, enterTickerName.get(), enterStockAmount.get(), 
                                                                                            enterStockDate.get()))
        addInvestButton.place(x=440, y=880, width=100)

        tk.Label(main, text = "Liquidate Position", font='Helvetica 16').place(x = 1410, y = 600)

        cursor.execute("SELECT * FROM currInvestment WHERE userID = %s", (userID,))
        curInvestment = cursor.fetchall()

        investmentTrns = tk.Label(main, text="Investment Ticker")
        investmentTrns.place(x=1425, y=640)
        #creates a dropdown box which contains the tranaction ids for the debts
        investCombobox = ttk.Combobox(main, values=[investment[1] for investment in curInvestment])
        investCombobox.place(x=1455, y=670, width=100)

        #creates the remove cash function, with boxes
        removeStockQuan = tk.Label(main, text="Quantity to Remove")
        removeStockQuan.place(x=1425, y=700)
        enterRemoveStockQuan = Entry(main, width=35)
        enterRemoveStockQuan.place(x=1455, y=730, width=100)

        #button which removes the debt
        removeDebtButton = tk.Button(main, text="Liquidate", command=lambda: remInvestment(userID, 
                                                                                        investCombobox.get(), float(enterRemoveStockQuan.get())))
        removeDebtButton.place(x=1420, y=780, width=100)

        helpObject = Balloon(main)
        helpObject.bind_widget(addTicker, balloonmsg="Enter the ticker of the stock you want to add to the database.")
        helpObject.bind_widget(addStockAmount, balloonmsg="Enter the number of shares you want to add to the database. Fractional shares are permitted.")
        helpObject.bind_widget(addStockDate, balloonmsg="Enter the date of the transaction. Format: YYYY-MM-DD")
        helpObject.bind_widget(addInvestButton, balloonmsg="Add an investment to the investment table.")
        helpObject.bind_widget(investmentTrns, balloonmsg="Select the investment you want to liquidate (remove).")
        helpObject.bind_widget(removeStockQuan, balloonmsg="Enter the number of shares you want to liquidate.")
        helpObject.bind_widget(removeDebtButton, balloonmsg="Liquidate the selected investment.")

        main.mainloop()

    except Exception as e: 
        tk.messagebox.showerror(title="Error", message="Error creating page: " + str(e))