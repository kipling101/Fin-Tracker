import tkinter as tk
import mysql.connector
from tkinter import *
from tkinter import messagebox
import datetime; from datetime import timedelta, datetime

userID = 1
totalDebt = 0

def calcDebt(userID,totalDebt):
    db = mysql.connector.connect(host ="localhost", user = "root", password = "pass123", db ="FinTracker")
    cursor = db.cursor()
    #retrieves current debt information for the user given by the userID
    cursor.execute("SELECT * FROM debtHoldings WHERE userID = %s", (userID,))
    curDebt = cursor.fetchall()

    today = datetime.today() #finds the current date

    for i in curDebt:
        #extracts the debt information from the tuple
        debtValue = i[1]
        debtName = i[2] #to be used for the visual interface
        debtDate = i[3]
        debtAPR = i[4]/100
        
        debtDate = datetime.strptime(debtDate, '%Y-%m-%d') #formats the debt data to a datetime object
        daysSince = (today - debtDate).days #finds the number of days since the debt was taken out

        #calculates the interest accrued on the debt using compound interest formula
        currDebtVal = float(debtValue)*((1+(debtAPR/365))**daysSince)
        print(currDebtVal)
        totalDebt += currDebtVal

    print("£",round(totalDebt,2))

calcDebt(userID, totalDebt)