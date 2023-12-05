import tkinter as tk
import mysql.connector
from tkinter import *
from tkinter import messagebox

#initialise variables, will be made inputs later
inputUsername = 'John'
inputPassword = 'pass234'
inputPasswordVerify = 'pass234'

def createAccount(inputUsername, inputPassword, inputPasswordVerify):

    #initialise database connection
    db = mysql.connector.connect(host ="localhost", user = "root", password = "pass123", db ="FinTracker")
    cursor = db.cursor() 

    #retrieves a list of usernames from the database where the username is equal to the inputted username
    #if they are the same then it returns a message saying the username already exists

    cursor.execute("SELECT * FROM Users WHERE name = %s", (inputUsername,))
    duplicateCheck = cursor.fetchall()

    if duplicateCheck:
        print("Username already exists, please try again.")
        return

    #checks if the inputted password and the inputted password verification are the same, if they are then it inserts the username and password into the database
    if inputPassword == inputPasswordVerify:
        cursor.execute("INSERT INTO Users (name, password) VALUES (%s, %s)", (inputUsername, inputPassword))
        db.commit()

        userID = cursor.lastrowid
        #creates a new user in the privileges table with the default privileges of 00 and the userID from the Users table
        cursor.execute("INSERT INTO privileges (userID, privLevel) VALUES (%s, %s)", (userID, 00))
        db.commit()

    else:
        print("Passwords do not match, please try again.")

createAccount(inputUsername, inputPassword, inputPasswordVerify)