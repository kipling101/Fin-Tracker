import tkinter as tk
from tkinter import *
import tkinter.ttk as ttk
import mysql.connector
import datetime
import datetime; from datetime import timedelta, datetime
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

#initialise variables, will be made inputs later
inputName = 'gfd'
inputAmount = 100
inputDate = '2020-02-03'
inputAPR = 1.2

removeName = 'gfdg'
removeReason = 'gfdoije'
removeAmount = 43
removeDate = '2020-01-03'
removeAPR = 1.2

totalCash = 0

userID = 1

db = mysql.connector.connect(host ="localhost", user = "root", password = "pass123", db ="FinTracker")
cursor = db.cursor()

def cashAdd(userID, inputName, inputAmount, inputDate, inputAPR):
    if inputDate > datetime.now().strftime('%Y-%m-%d') or inputDate == "":
        tk.messagebox.showerror(title="Add Cash", message="Error: Invalid Date.")
        return
    if inputName == "":
        tk.messagebox.showerror(title="Add Cash", message="Error: Invalid Name.")
        return
    #inserts the inputted data into the cash table
    cursor.execute("INSERT INTO cash (userID, trnsName, trnsAmount, trnsDate, trnsAPR) VALUES (%s, %s, %s, %s, %s)", 
                   (userID, inputName, float(inputAmount), inputDate, inputAPR))
    db.commit()
    tk.messagebox.showinfo(title="Add Cash", message="Cash added successfully!")

def cashRemove(userID, removeName, removeAmount, removeAPR):
    #inverts the values to add the cash and apr
    removeAmount = removeAmount * -1
    removeAPR = removeAPR * -1
    removeDate = datetime.now().strftime('%Y-%m-%d')
    cashAdd(userID, removeName, removeAmount, removeDate, removeAPR)

def calcCash(userID):
    dateList = []

    #retrieves current cash information for the user given by the userID
    cursor.execute("SELECT * FROM cash WHERE userID = %s", (userID,))
    curCash = cursor.fetchall()

    #adds the cash information to the list of cash
    curCash.sort(key=lambda x: datetime.strptime(x[3], '%Y-%m-%d'))
    #get todays date, as well as the final date
    startDate = datetime.strptime(curCash[0][3], '%Y-%m-%d')
    endDate = datetime.today()

    runningTotalEveryDay = []
    dateList = []

    #iterates over every day in the list, and calculates the total cash on that day
    currentDate = startDate
    while currentDate <= endDate:
        runningTotal = 0
        #checks to see if the day the cash was taken out is before the current date in the loop
        for i in range(len(curCash)):
            #only process cash for the input userID
            if curCash[i][0] == userID:
                cashDate = datetime.strptime(curCash[i][3], '%Y-%m-%d')
                #only adds the code if the cash was taken out before the current date
                if cashDate <= currentDate:
                    daysSince = (currentDate - cashDate).days
                    runningTotal += float(curCash[i][2]) * ((1 + ((float(curCash[i][4]) / 100) / 365)) ** daysSince)
        runningTotalEveryDay.append(runningTotal)
        dateList.append(currentDate)
        currentDate += timedelta(days=1)

    return [runningTotalEveryDay, dateList]

#append to a 2d array, then plot the array
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
cashData = calcCash(userID)
a.plot(cashData[1], cashData[0], ls='-')
a.set_title("Value")
a.set_xlabel("Date")

#creates the canvas for the graph to be displayed on
canvas = FigureCanvasTkAgg(f, master=main)
canvas.draw()
canvas.get_tk_widget().pack()

cursor.execute("SELECT * FROM cash WHERE userID = %s", (userID,))
curCash = cursor.fetchall()

#creates the add cash function, with boxes
tk.Label(main, text="Add Cash", font='Helvetica 16').place(x=20, y=600)
#creates the add cash function, with boxes
addCashName = tk.Label(main, text="Name")
addCashName.place(x=50, y=640)
enterCashName = Entry(main, width=35)
enterCashName.place(x=75, y=670, width=100)

addCashAmount = tk.Label(main, text="Value")
addCashAmount.place(x=50, y=700)
enterCashAmount = Entry(main, width=35)
enterCashAmount.place(x=75, y=730, width=100)

addCashDate = tk.Label(main, text="Date")
addCashDate.place(x=50, y=760)
enterCashDate = Entry(main, width=35)
enterCashDate.place(x=75, y=790, width=100)

addCashAPR = tk.Label(main, text="APR")
addCashAPR.place(x=50, y=820)
enterCashAPR = Entry(main, width=35)
enterCashAPR.place(x=75, y=850, width=100)
#button which adds the cash
addCashButton = tk.Button(main, text="Add Cash", command=lambda: cashAdd(userID, enterCashName.get(), enterCashAmount.get(), enterCashDate.get(), 
                                                                         enterCashAPR.get()))
addCashButton.place(x=75, y=880, width=100)

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
removeCashButton = tk.Button(main, text="Remove Cash", command=lambda: cashRemove(userID, enterRemoveCashName.get(), 
                                                                                  float(enterRemoveCashAmount.get()), float(enterRemoveCashAPR.get())))
removeCashButton.place(x=1000, y=840, width=100)

main.mainloop()