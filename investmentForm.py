import yfinance as yf
import datetime; from datetime import timedelta, datetime
import mysql.connector; import pytz
import tkinter as tk; from tkinter import messagebox; from tkinter import Entry; from tkinter import ttk; from tkinter import tix; from tkinter.tix import Balloon
import matplotlib; matplotlib.use('TkAgg'); from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg; from matplotlib.figure import Figure
import menu

db = mysql.connector.connect(host ="localhost", user = "root", password = "pass123", db ="FinTracker")
cursor = db.cursor()

def openInvestmentForm(userID):
    
    def addInvestment(userID, addStockTicker, addShareNum, addShareDate):
        try:
            #checks if the inputted data is valid
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
            #displays a success message
            tk.messagebox.showinfo("Success", "Investment added successfully!")

        except mysql.connector.errors.DataError:
            tk.messagebox.showerror(title="Add Investment", message="Error: Entry Data.")
        except Exception as e:
            tk.messagebox.showerror(title="Add Investment", message="Error: " + str(e))

    def remInvestment(userID, remStockTicker, remShareNum):
        try:
            #checks if there is a investment that matches the inputted data
            remInvSQL = "SELECT * FROM currInvestment WHERE userID = %s AND stockTicker = %s"
            cursor.execute(remInvSQL, (userID, remStockTicker,))
            results = cursor.fetchall()

            #if a result is returned, deletes the investment from the database
            if results:
                newShareNum = remShareNum * -1 #inverts the value for removing shares from the database
                
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
            calcInvSQL = "SELECT * FROM currInvestment WHERE userID = %s"
            cursor.execute(calcInvSQL, (userID,))
            curHolding = cursor.fetchall()

            #finds the first date of purchase
            earliestDate = min(datetime.strptime(i[3], '%Y-%m-%d') for i in curHolding)
            dateOverTime = [earliestDate + timedelta(days=i) for i in range((datetime.now() - earliestDate).days + 1)]
            valOverTime = [0] * len(dateOverTime)  #creates a list of 0s the same length as the dateOverTime list

            #creates a list of dates from the earliest date to the current date
            
            for i in curHolding: #iterates over each investment holding
                #strips important information from the database
                stockTicker = i[1]
                sharesHeld = i[2]
                datePur = datetime.strptime(i[3], '%Y-%m-%d')

                currDate = datetime.strptime(str(datetime.now()), '%Y-%m-%d %H:%M:%S.%f')
                stockInfo = yf.Ticker(stockTicker)
                #gets the stock price from the date of purchase to the current date
                stockPrice = stockInfo.history(period="1d", start=datePur, end=currDate) 

                #creates a list of the value of the investment over time, only adding the value if it is not already present, 
                #otherwise it adds the value to the existing value
                for j in range(len(dateOverTime)):
                    if dateOverTime[j] >= datePur and dateOverTime[j] <= currDate:
                        try:
                            valOverTime[j] += stockPrice['Open'][dateOverTime[j]] * sharesHeld
                        except Exception as e:
                            continue
            return [valOverTime, dateOverTime]
        except Exception as e: 
            tk.messagebox.showerror(title="Error", message="Error: " + str(e))


    main = tix.Tk()
    main.title("Investment")
    main.state('zoomed') #sets the desired width and height of the image

    cursor.execute("SELECT * FROM currinvestment WHERE userID = %s", (userID,))
    curInvestment = cursor.fetchall()

    #creates the menu
    menu.createMenu(main, userID)
    if len(curInvestment) != 0:

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
        columns = ('Ticker', 'Quantity', 'Date', 'Transaction Number')  #column names

        #create columns
        tree['columns'] = columns

        for column in columns:
            tree.heading(column, text=column)
            tree.column(column, width=60)

        #adds only rows 1,2,4,5 to the table
        for i, row in enumerate(curInvestment):
            tree.insert('', 'end', values=(row[1], row[2], row[3], row[4]))
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
    addInvestButton.place(x=440, y=840, width=120)

    tk.Label(main, text = "Liquidate Position", font='Helvetica 16').place(x = 1410, y = 600)

    cursor.execute("SELECT * FROM currInvestment WHERE userID = %s", (userID,))
    curInvestment = cursor.fetchall()

    investmentTrns = tk.Label(main, text="Investment Ticker")
    investmentTrns.place(x=1425, y=640)
    #creates a dropdown box which contains the tranaction ids for the investments
    investCombobox = ttk.Combobox(main, values=[investment[1] for investment in curInvestment])
    investCombobox.place(x=1455, y=670, width=100)

    #creates the remove investment function, with boxes
    removeStockQuan = tk.Label(main, text="Quantity to Remove")
    removeStockQuan.place(x=1425, y=700)
    enterRemoveStockQuan = Entry(main, width=35)
    enterRemoveStockQuan.place(x=1455, y=730, width=100)

    #button which removes the investments
    removeStockButton = tk.Button(main, text="Liquidate", command=lambda: remInvestment(userID, 
                                                                                    investCombobox.get(), float(enterRemoveStockQuan.get())))
    removeStockButton.place(x=1420, y=780, width=120)

    #creates help boxes for the user
    helpObject = Balloon(main)
    helpObject.bind_widget(enterTickerName, balloonmsg="Enter the ticker of the stock you want to add to the database.")
    helpObject.bind_widget(enterStockAmount, balloonmsg="Enter the number of shares you want to add to the database. Fractional shares are permitted.")
    helpObject.bind_widget(enterStockDate, balloonmsg="Enter the date of the transaction. Format: YYYY-MM-DD")
    helpObject.bind_widget(addInvestButton, balloonmsg="Add an investment to the investment table.")
    helpObject.bind_widget(investmentTrns, balloonmsg="Select the investment you want to liquidate (remove).")
    helpObject.bind_widget(enterRemoveStockQuan, balloonmsg="Enter the number of shares you want to liquidate.")
    helpObject.bind_widget(removeStockButton, balloonmsg="Liquidate the selected investment.")

    main.mainloop()
