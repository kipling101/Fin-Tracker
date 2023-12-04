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

    cursor.execute("SELECT * FROM Users WHERE name = %s", (inputUsername,))
    duplicateCheck = cursor.fetchall()

    if duplicateCheck:
        print("Username already exists, please try again.")
        return
    
    if inputPassword == inputPasswordVerify:
        cursor.execute("INSERT INTO Users (name, password) VALUES (%s, %s)", (inputUsername, inputPassword))
        db.commit()

        userID = cursor.lastrowid
        
        cursor.execute("INSERT INTO privileges (userID, privLevel) VALUES (%s, %s)", (userID, 1))
        db.commit()

    else:
        print("Passwords do not match, please try again.")

createAccount()