import tkinter as tk
import mysql.connector
from tkinter import *
from tkinter import messagebox

inputName = 'gfdg'
inputAmount = 43
inputDate = 12
inputAPR = 1.2

removeName = 'gfdg'
removeReason = 'gfdoijew'
removeAmount = 43
removeDate = 12
removeAPR = 1.2
userID = 1



def cashAdd(userID, inputName, inputAmount, inputDate, inputAPR):
    db = mysql.connector.connect(host ="localhost", user = "root", password = "pass123", db ="FinTracker")
    cursor = db.cursor() 

    cashSQL = "INSERT INTO cash (userID, trnsName, trnsAmount, trnsDate, trnsAPR) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(cashSQL, (userID, inputName, inputAmount, inputDate, inputAPR))
    db.commit()

def cashRemove(userID, inputName, inputAmount, inputDate, inputAPR):
    db = mysql.connector.connect(host ="localhost", user = "root", password = "pass123", db ="FinTracker")
    cursor = db.cursor()

    cashDeleSQL = "SELECT * FROM cash WHERE userID = %s AND trnsName = %s AND trnsAmount = %s AND trnsDate = %s AND trnsAPR = %s"
    cursor.execute(cashDeleSQL, (userID, inputName, inputAmount, inputDate, inputAPR))
    results = cursor.fetchall()
    print(results)

    if results:
        cashDelSQL = "DELETE FROM cash WHERE userID = %s AND trnsName = %s AND trnsAmount = %s AND trnsDate = %s AND trnsAPR = %s"
        cursor.execute(cashDelSQL, (userID, inputName, inputAmount, inputDate, inputAPR))
        db.commit()

    else: print("No such cash transaction exists, please verify data inputted and try again.")

cashAdd(userID, inputName, inputAmount, inputDate, inputAPR)