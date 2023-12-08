import tkinter as tk
import mysql.connector
from tkinter import *
from tkinter import messagebox
import datetime; from datetime import timedelta, datetime

userID = 1
totalDebt = 0
addDebtName = 'Credit Card'
addDebtAmount = 1000.0
addDebtDate = '2020-01-03'
addDebtAPR = 19.5

remDebtName = 'Credit Card'
remDebtAPR = 19.5

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

def addDebt(userID, addDebtAmount, addDebtName, addDebtDate, addDebtAPR):
    db = mysql.connector.connect(host ="localhost", user = "root", password = "pass123", db ="FinTracker")
    cursor = db.cursor()

    #inserts the inputted data into the debtHoldings table
    addDebtSQL = "INSERT INTO debtHoldings (userID, addDebtAmount, addDebtName, addDebtDate, addDebtAPR) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(addDebtSQL, (userID, addDebtAmount, addDebtName, addDebtDate, addDebtAPR,))
    db.commit()

    print("Debt successfull added!")

def remDebt(userID, remDebtName, remDebtAPR):
    db = mysql.connector.connect(host ="localhost", user = "root", password = "pass123", db ="FinTracker")
    cursor = db.cursor()

    #checks if there is a debt that matches the inputted data
    cursor.execute("SELECT * FROM debtHoldings WHERE userID = %s AND debtName = %s AND APR = %s", (userID, remDebtName, remDebtAPR))
    presCheck = cursor.fetchall()

    #if a result is returned, deletes the debt from the database 
    if presCheck:
        cursor.execute("DELETE FROM debtHoldings WHERE userID = %s AND debtName = %s AND APR = %s", (userID, remDebtName, remDebtAPR,))
        db.commit()

        print("Debt removed successfully!")

    else:    
        print("No such debt exists, please verify data inputted and try again.")