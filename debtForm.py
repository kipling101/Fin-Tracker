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
        debtName = i[2] #to be used for the visual interface
       
        debtDate = datetime.strptime(i[3], '%Y-%m-%d') #formats the debt data to a datetime object
        daysSince = (today - debtDate).days #finds the number of days since the debt was taken out

        #calculates the interest accrued on the debt using compound interest formula, and adds it to the total debt
        totalDebt += float(i[1])*((1+((i[4]/100)/365))**daysSince)

    print("£",round(totalDebt,2))

calcDebt(userID, totalDebt)