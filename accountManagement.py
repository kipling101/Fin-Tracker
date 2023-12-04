import tkinter as tk
import mysql.connector
from tkinter import *
from tkinter import messagebox

def permModify():
    userID = 1

    db = mysql.connector.connect(host ="localhost", user = "root", password = "pass123", db ="FinTracker")
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Users WHERE id = %s", (userID,))
    userID = cursor.fetchall()

    if userID:
        newPrivLevel = 14
        cursor.execute("UPDATE privileges SET privLevel = %s WHERE userID = %s", (newPrivLevel, userID[0][0],))
        db.commit()
        print("Privilege level updated.")

permModify()