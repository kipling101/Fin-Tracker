import tkinter as tk
import mysql.connector
from tkinter import *
from tkinter import messagebox

#initialise variables, will be made inputs later
inputName = 'gfdg'
inputAmount = 43
inputDate = 12
inputAPR = 1.2

removeName = 'gfdg'
removeReason = 'gfdoije'
removeAmount = 43
removeDate = 12
removeAPR = 1.2

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

cashAdd(userID, inputName, inputAmount, inputDate, inputAPR)