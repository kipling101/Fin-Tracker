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
import privCheck as pc; import menu

db = mysql.connector.connect(host ="localhost", user = "root", password = "pass123", db ="FinTracker")
cursor = db.cursor()

def openDebtForm(userID):
    totalDebt = 0
    
    def calcDebt(userID, totalDebt):
        #retrieves current debt information for the user given by the userID
        cursor.execute("SELECT * FROM debtHoldings WHERE userID = %s", (userID,))
        curDebt = cursor.fetchall()
        try:
            today = datetime.today() #finds the current date

            for i in curDebt:
                debtName = i[2] #to be used for the visual interface
            
                debtDate = datetime.strptime(i[3], '%Y-%m-%d') #formats the debt data to a datetime object
                daysSince = (today - debtDate).days #finds the number of days since the debt was taken out

                #calculates the interest accrued on the debt using compound interest formula, and adds it to the total debt
                totalDebt += float(i[1])*((1+((i[4]/100)/365))**daysSince)

            #adds the debt information to the list of debts
            curDebt.sort(key=lambda x: datetime.strptime(x[3], '%Y-%m-%d'))
            #gets todays date, as well as the final date
            startDate = datetime.strptime(curDebt[0][3], '%Y-%m-%d')
            endDate = datetime.today()

            runningTotalEveryDay = []; dateList = []

            #iterates over every day in the list, and calculates the total debt on that day
            currentDate = startDate
            while currentDate <= endDate:
                runningTotal = 0
                #checks to see if the day the debt was taken out is before the current date in the loop
                for i in range(len(curDebt)):
                    #only process debts for the input userID, incase of SQL error
                    if curDebt[i][0] == userID:
                        debtDate = datetime.strptime(curDebt[i][3], '%Y-%m-%d')
                        #only adds the value if the debt was taken out before the current date
                        if debtDate <= currentDate:
                            daysSince = (currentDate - debtDate).days
                            runningTotal += float(curDebt[i][1])*((1+((curDebt[i][4]/100)/365))**daysSince)
                runningTotalEveryDay.append(runningTotal)
                dateList.append(currentDate)
                currentDate += timedelta(days=1)

            return [runningTotalEveryDay, dateList]
        
        except ValueError:
            tk.messagebox.showerror("Error", "An error has occured, please try again.")

    def addDebt(userID, addDebtAmount, addDebtName, addDebtDate, addDebtAPR):

        if userID and addDebtAmount and addDebtName and addDebtDate and addDebtAPR:
            if addDebtDate > datetime.now().strftime('%Y-%m-%d'):
                tk.messagebox.showerror("Error", "Please enter a valid date!")
                return
            if float(addDebtAmount) < 0 and addDebtAmount.replace(".", "").isnotnumeric():
                tk.messagebox.showerror("Error", "Please enter a valid amount!")
                return
            if float(addDebtAPR) < 0:
                tk.messagebox.showerror("Error", "Please enter a valid APR!")
                return
            if len(addDebtName) < 2 or len(addDebtName) > 20:
                tk.messagebox.showerror("Error", "Please enter a valid name!")
                return
            
            #inserts the inputted data into the debtHoldings table
            addDebtSQL = "INSERT INTO debtHoldings (userID, debtValue, debtName, paymentDate, APR) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(addDebtSQL, (userID, addDebtAmount, addDebtName, addDebtDate, addDebtAPR,))
            db.commit()

        else: 
            tk.messagebox.showerror("Error", "Please fill in all fields!")

        tk.messagebox.showinfo("Success", "Debt added successfully!")

    def remDebt(userID, trnsNum, removeAmount):
        #checks if there is a debt that matches the inputted data
        cursor.execute("SELECT * FROM debtHoldings WHERE userID = %s AND transactionNumber = %s", (userID, trnsNum))
        debts = cursor.fetchall()

        for debt in debts:
            #calculates the current value of the debt with compound interest
            debtValue = float(debt[1])
            debtDate = datetime.strptime(debt[3], '%Y-%m-%d')
            APR = float(debt[4])
            daysSince = (datetime.now() - debtDate).days
            currentValue = debtValue * ((1 + (APR / 100 / 365)) ** daysSince)

            #calculates the new value of the debt after removing the specified amount
            newValue = currentValue - float(removeAmount)
            if newValue < 0:
                newValue = 0

            #updates the debt value in the database
            cursor.execute("UPDATE debtHoldings SET debtValue = %s WHERE userID = %s AND transactionNumber = %s", (newValue, userID, trnsNum))
            db.commit()  

        if debts:
            tk.messagebox.showinfo("Success", "Debt removed successfully!")
        else:    
            tk.messagebox.showerror("Error", "Debt not found!")

    cursor.execute("SELECT * FROM debtHoldings WHERE userID = %s", (userID,))
    curDebt = cursor.fetchall()

    main = tk.Tk()
    main.state('zoomed')
    main.title("FinTracker")
    #creates the menu interface
    menu.createMenu(main, userID)
    width, height = 100, 100

    figSize = 4,4

    #code for creating the first graph which dispays debt over time
    f = Figure(figsize=figSize, dpi=100)
    debtOvTime = f.add_subplot(111)

    #plots the data on the graph
    calcDebt2 = calcDebt(userID, totalDebt)
    debtOvTime.plot(calcDebt2[1], calcDebt2[0], ls = '-')
    debtOvTime.set_title("Debt Amount")
    debtOvTime.set_xlabel("Date")
    debtOvTime.set_ylabel("Value (£)")

    #creates the canvas for the graph to be displayed on
    canvas1=FigureCanvasTkAgg(f,master=main)
    canvas1.draw()
    canvas1.get_tk_widget().pack()
    #creates interface which allows users to add or remove debt
    tk.Label(main, text = "Add Debt", font='Helvetica 16').place(x = 430, y = 600)

    addDebtName = tk.Label(main, text="Name")
    addDebtName.place(x=445, y=640)
    enterDebtName = Entry(main, width=35)
    enterDebtName.place(x=470, y=670, width=100)

    addDebtAmount = tk.Label(main, text="Value")
    addDebtAmount.place(x=445, y=700)
    enterDebtAmount = Entry(main, width=35)
    enterDebtAmount.place(x=470, y=730, width=100)

    addDebtDate = tk.Label(main, text="Date")
    addDebtDate.place(x=445, y=760)
    enterDebtDate = Entry(main, width=35)
    enterDebtDate.place(x=470, y=790, width=100)

    addDebtAPR = tk.Label(main, text="APR")
    addDebtAPR.place(x=445, y=820)
    enterDebtAPR = Entry(main, width=35)
    enterDebtAPR.place(x=470, y=850, width=100)

    addDebtButton = tk.Button(main, text="Add Debt", command=lambda: addDebt(userID, enterDebtAmount.get(), enterDebtName.get(), enterDebtDate.get(), enterDebtAPR.get()))
    addDebtButton.place(x=440, y=900, width=100)

    tk.Label(main, text = "Remove Debt", font='Helvetica 16').place(x = 1410, y = 600)

    debtSelLabel = tk.Label(main, text="Debt Transaction Number")
    debtSelLabel.place(x=1425, y=640)
    debtCombobox = ttk.Combobox(main, values=[debt[5] for debt in curDebt])
    debtCombobox.place(x=1455, y=670, width=100)
    
    removeAmountLabel = tk.Label(main, text="Amount to Remove")
    removeAmountLabel.place(x=1425, y=700)
    enterRemoveAmount = tk.Entry(main, width=35)
    enterRemoveAmount.place(x=1455, y=730, width=100)

    removeDebtButton = tk.Button(main, text="Remove Debt", command=lambda: remDebt(userID, debtCombobox.get(), enterRemoveAmount.get()))
    removeDebtButton.place(x=1420, y=780, width=100)

    main.mainloop()