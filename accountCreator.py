import tkinter as tk
import mysql.connector
from tkinter import *
from tkinter import messagebox

def createAccount():
    inputUsername = 'John'
    inputPassword = 'pass234'
    inputPasswordVerify = 'pass234'

    db = mysql.connector.connect(host ="localhost", user = "root", password = "pass123", db ="FinTracker")
    cursor = db.cursor() 
    #check user does not exist already
    if inputPassword == inputPasswordVerify:
        accCreateSQL = "INSERT INTO Users (name, password) VALUES (%s, %s)"
        cursor.execute(accCreateSQL, (inputUsername, inputPassword))
        db.commit()

        userID = cursor.lastrowid
        
        privCreateSQL = "INSERT INTO privileges (userID, privLevel) VALUES (%s, %s)"
        cursor.execute(privCreateSQL, (userID, 1))
        db.commit()

    else:
        print("Passwords do not match, please try again.")

createAccount()