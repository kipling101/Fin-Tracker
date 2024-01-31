import tkinter as tk
from tkinter import *
from tkinter import messagebox
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

    #inserts the inputted data into the cash table
    cursor.execute("INSERT INTO cash (userID, trnsName, trnsAmount, trnsDate, trnsAPR) VALUES (%s, %s, %s, %s, %s)", 
                   (userID, inputName, inputAmount, inputDate, inputAPR))
    db.commit()


def cashRemove(userID, removeName, removeAmount, removeDate, removeAPR):

    #checks if there is a cash transaction that matches the inputted data
    cursor.execute("SELECT * FROM cash WHERE userID = %s AND trnsName = %s AND trnsAmount = %s AND trnsDate = %s AND trnsAPR = %s", 
                   (userID, removeName, removeAmount, removeDate, removeAPR))
    results = cursor.fetchall()
    #if a result is returned, deletes the cash transaction from the database
    if results:
        cursor.execute("DELETE FROM cash WHERE userID = %s AND trnsName = %s AND trnsAmount = %s AND trnsDate = %s AND trnsAPR = %s", 
                       (userID, removeName, removeAmount, removeDate, removeAPR))
        db.commit()

    else: print("No such cash transaction exists, please verify data inputted and try again.")

def calcCash(userID,totalCash):
    
    #retrieves current debt information for the user given by the userID
    cursor.execute("SELECT * FROM cash WHERE userID = %s", (userID,))
    curCash = cursor.fetchall()

    today = datetime.today() #finds the current date

    for i in curCash:
        #extracts the cash information from the tuple
        cashName = i[1] #to be used for the visual interface

        cashDate = datetime.strptime(i[3], '%Y-%m-%d') #formats the cash data to a datetime object
        daysSince = (today - cashDate).days #finds the number of days since the cash was added to the account
        
        #calculates the interest accrued on the cash using compound interest formula, and adds it to the total debt
        totalCash += float(i[2])*((1+((i[4]/100)/365))**daysSince)

    print("£",round(totalCash,2))

def valOverTime():
    runningTotalList = []
    date = []
    cursor.execute("SELECT trnsAmount FROM cash WHERE userID = %s", (userID,))
    cashAmount = cursor.fetchall()

    cursor.execute("SELECT trnsDate FROM cash WHERE userID = %s", (userID,))
    cashDate = cursor.fetchall()

    #calculates the current value day by day by subtracting any money removed from the value and adding any money added
    #to the value
    runningTotal = 0

    for i in range(len(cashAmount)):
        runningTotal += cashAmount[i][0]
        date.append(cashDate[i][0])
        runningTotalList.append(runningTotal)
        
    return [runningTotalList, date]

#append to a 2d array, then plot the array
valOverTime()

main = tk.Tk()
main.title("Modify Permissions")
main.geometry("500x500")  # Set your desired width and height
def __init__(master):
    # Create a Matplotlib figure and plot with the specified size
    f = Figure(figsize=(5,5), dpi=100)
    a = f.add_subplot(111)

    a.plot(valOverTime()[1], valOverTime()[0], ls = '-')
    canvas1=FigureCanvasTkAgg(f,master=main)
    canvas1.draw()
    canvas1.get_tk_widget().pack(side="top",fill='both',expand=True)

#IDK WHAT IS GOING ON HERE
    
__init__(master=main)
main.mainloop()