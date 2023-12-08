import tkinter as tk
import mysql.connector
from tkinter import *
from tkinter import messagebox

#initialise variables, will be made inputs later
userID = 1

def permModify(userID):
    
    #initialise database connection
    db = mysql.connector.connect(host ="localhost", user = "root", password = "pass123", db ="FinTracker")
    cursor = db.cursor()
    #finds the current privilege level of the user given by the userID
    cursor.execute("SELECT privLevel FROM privileges WHERE userid = %s", (userID,))
    curPrivLevel = cursor.fetchall()
    #verifies userID is present
    if userID:

        newPrivLevel = 11
        #sets the privilege level of the user, given by the userID, to the new privilege level
        cursor.execute("UPDATE privileges SET privLevel = %s WHERE userID = %s", (newPrivLevel, userID,))
        db.commit()

        print("Privilege level updated.")

    else: print("User not found.")
    
permModify(userID)