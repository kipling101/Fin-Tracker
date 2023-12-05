import tkinter as tk
import mysql.connector
from tkinter import *
from tkinter import messagebox

userID = 1

def addDebt(userID):
    db = mysql.connector.connect(host ="localhost", user = "root", password = "pass123", db ="FinTracker")
    cursor = db.cursor()
    #create debt SQL first
    cursor.execute("SELECT * FROM  WHERE userID = %s", (userID,))