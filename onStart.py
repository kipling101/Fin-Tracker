
import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter import messagebox
import mysql.connector
import yfinance as yf
import datetime
from datetime import timedelta
from datetime import datetime
from dateutil.relativedelta import relativedelta
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import calendar


db = mysql.connector.connect(host="localhost", user="root", password="pass123", db="FinTracker")
cursor = db.cursor()

userID = 1

def onStart(userID):
    cursor.execute("SELECT * FROM payments WHERE userid = %s", (userID,))
    payments = cursor.fetchall()
    
    cursor.execute("SELECT * FROM lastAccessed WHERE userid = %s", (userID,))
    lastAccessed = cursor.fetchall()

    if len(lastAccessed) == 0:
        cursor.execute("INSERT INTO lastAccessed (userid, date) VALUES (%s, %s)", (userID, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        db.commit()

        cursor.execute("SELECT * FROM lastAccessed WHERE userid = %s", (userID,))
        lastAccessed = cursor.fetchall()
        
    for i in range(len(payments)):
        timeNow = datetime.now()
        if datetime.strptime(str(payments[i][2]).split('.')[0], '%Y-%m-%d %H:%M:%S') < timeNow:
                
            daySincePayLess = (timeNow - datetime.strptime(payments[i][5], '%Y-%m-%d %H:%M:%S')).days - 30.437
            daySincePay = (timeNow - datetime.strptime(payments[i][5], '%Y-%m-%d %H:%M:%S')).days; print(payments[i][4], payments[i][1]) 
            monthCompound = payments[i][1]*(1+((payments[i][4]/100)/365.25))**(daySincePay) - payments[i][1]*(1+((payments[i][4]/100)/365.25))**(daySincePayLess)
            print(daySincePayLess, daySincePay, monthCompound)
            cursor.execute("INSERT INTO cash (userID, trnsName, trnsAmount, trnsDate, trnsAPR) VALUES (%s, %s, %s, %s, %s)", 
                (userID, "Interest", monthCompound, datetime.now().strftime('%Y-%m-%d'), 0))
            offsetDate = datetime.now() + relativedelta(months=+1)

            cursor.execute("UPDATE payments SET paymentDate = %s WHERE userid = %s and paymentID = %s", 
                    ((datetime.strftime(datetime.now() + relativedelta(months=+1), '%Y-%m-%d %H:%M:%S')), userID, payments[i][3]))
            db.commit()

onStart(userID)
