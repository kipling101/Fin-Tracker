import tkinter as tk
import mysql.connector
from tkinter import *
from tkinter import messagebox
import datetime; from datetime import timedelta, datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tkinter import ttk
import pandas as pd

userID = 1

def __main__(userID):
    totalDebt = 0
    db = mysql.connector.connect(host ="localhost", user = "root", password = "pass123", db ="FinTracker")
    cursor = db.cursor()

    def calcDebt(userID, totalDebt):
        #retrieves current debt information for the user given by the userID
        cursor.execute("SELECT * FROM debtHoldings WHERE userID = %s", (userID,))
        curDebt = cursor.fetchall()

        today = datetime.today() #finds the current date

        for i in curDebt:
            #extracts the debt information from the tuple
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
                #only process debts for the input userID
                if curDebt[i][0] == userID:
                    debtDate = datetime.strptime(curDebt[i][3], '%Y-%m-%d')
                    #only adds the code if the debt was taken out before the current date
                    if debtDate <= currentDate:
                        daysSince = (currentDate - debtDate).days
                        runningTotal += float(curDebt[i][1])*((1+((curDebt[i][4]/100)/365))**daysSince)
            runningTotalEveryDay.append(runningTotal)
            dateList.append(currentDate)
            currentDate += timedelta(days=1)

        return [runningTotalEveryDay, dateList]

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
    main.title("Debt")
    main.geometry("500x500")

    width, height = 100, 100

    #converts from px to inches
    figsize = 1,1

    #creates the window for the graph of a set size
    f = Figure(figsize=figsize, dpi=100)
    #adds a subplot to the window
    a = f.add_subplot(111)
    calcDebt = calcDebt(userID, totalDebt)
    #plots the data on the graph
    a.plot(calcDebt(userID,totalDebt)[1], calcDebt(userID,totalDebt)[0], ls = '-')

    a.set_title("Debt Amount")
    a.set_xlabel("Date")
    a.set_ylabel("Value (£)")

    #creates the canvas for the graph to be displayed on
    canvas1=FigureCanvasTkAgg(f,master=main)
    canvas1.draw()
    canvas1.get_tk_widget().pack()

    #creates the add debt function, with boxes
    tk.Label(main, text = "Add Debt", font='Helvetica 16').place(x = 20, y = 600)

    addDebtName = tk.Label(main, text="Name")
    addDebtName.place(x=50, y=640)
    enterDebtName = Entry(main, width=35)
    enterDebtName.place(x=75, y=670, width=100)

    addDebtAmount = tk.Label(main, text="Value")
    addDebtAmount.place(x=50, y=700)
    enterDebtAmount = Entry(main, width=35)
    enterDebtAmount.place(x=75, y=730, width=100)

    addDebtDate = tk.Label(main, text="Date")
    addDebtDate.place(x=50, y=760)
    enterDebtDate = Entry(main, width=35)
    enterDebtDate.place(x=75, y=790, width=100)

    addDebtAPR = tk.Label(main, text="APR")
    addDebtAPR.place(x=50, y=820)
    enterDebtAPR = Entry(main, width=35)
    enterDebtAPR.place(x=75, y=850, width=100)

    addDebtButton = tk.Button(main, text="Add Debt", command=lambda: addDebt(userID, enterDebtAmount.get(), enterDebtName.get(), enterDebtDate.get(), enterDebtAPR.get()))
    addDebtButton.place(x=75, y=880, width=100)

    tk.Label(main, text = "Remove Debt", font='Helvetica 16').place(x = 1000, y = 600)

    #creates an entry field for the user to input the amount they want ro remove
    enterRemoveAmount = tk.Entry(main, width=35)
    enterRemoveAmount.place(x=1000, y=700, width=100)
    #creates a dropdown box which contains the tranaction ids for the debts
    debtCombobox = ttk.Combobox(main, values=[debt[5] for debt in curDebt])
    debtCombobox.place(x=1000, y=650, width=100)
    #button which removes the debt
    removeDebtButton = tk.Button(main, text="Remove Debt", command=lambda: remDebt(userID, debtCombobox.get(), enterRemoveAmount.get())).place(x=1000, y=750, width=100)

    main.mainloop()