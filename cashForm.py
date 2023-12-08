import tkinter as tk
import mysql.connector
from tkinter import *
from tkinter import messagebox
import datetime; from datetime import timedelta, datetime

#initialise variables, will be made inputs later
inputName = 'gfdg'
inputAmount = 43
inputDate = '2020-01-03'
inputAPR = 1.2

removeName = 'gfdg'
removeReason = 'gfdoije'
removeAmount = 43
removeDate = '2020-01-03'
removeAPR = 1.2

totalCash = 0

userID = 1

def cashAdd(userID, inputName, inputAmount, inputDate, inputAPR):
    #initialise database connection
    db = mysql.connector.connect(host ="localhost", user = "root", password = "pass123", db ="FinTracker")
    cursor = db.cursor() 
    #inserts the inputted data into the cash table
    cursor.execute("INSERT INTO cash (userID, trnsName, trnsAmount, trnsDate, trnsAPR) VALUES (%s, %s, %s, %s, %s)", 
                   (userID, inputName, inputAmount, inputDate, inputAPR))
    db.commit()

def cashRemove(userID, removeName, removeAmount, removeDate, removeAPR):
    #initialise database connection
    db = mysql.connector.connect(host ="localhost", user = "root", password = "pass123", db ="FinTracker")
    cursor = db.cursor()
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
    db = mysql.connector.connect(host ="localhost", user = "root", password = "pass123", db ="FinTracker")
    cursor = db.cursor()
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

calcCash(userID,totalCash)