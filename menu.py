import tkinter as tk; from tkinter import ttk; from tkinter import *; from tkinter import messagebox
import mysql.connector
import yfinance as yf
import datetime; from datetime import timedelta; from datetime import datetime; from dateutil.relativedelta import relativedelta
import matplotlib; import matplotlib.pyplot as plt; matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg; from matplotlib.figure import Figure

userID = 1

def openHomePage(userID):
    print("User ID")

def openCashForm(userID):
    print("cash Page")

def openDebtForm(userID):
    print("debt Form")

def openAccountMgmForm(userID):
    print("account Form")


def createMenu(root, userID):
    buttonFrame = tk.Frame(root)
    buttonFrame.pack(side="left")

    home = tk.Button(buttonFrame, text ="Home", command = lambda: [root.destroy(), openHomePage(userID)], width=25, height = 10)
    home.grid(row=0, sticky = "W")

    cash = tk.Button(buttonFrame, text ="Cash", command = lambda: [print("Hi"), openCashForm(userID)], width=25, height = 10)
    cash.grid(row=1, sticky = "W")

    debt = tk.Button(buttonFrame, text ="Debt", command = lambda: [print("Hi"), openDebtForm(userID)], width=25, height = 10)
    debt.grid(row=2, sticky = "W")

    padding = tk.Label(buttonFrame, text = " ", width=25, height = 17)
    padding.grid(row=3, sticky = "W")

    account = tk.Button(buttonFrame, text ="Account", command = lambda: [root.destroy(), openAccountMgmForm(userID)], width=25, height = 6)
    account.grid(row=4, sticky = "W")


main = tk.Tk()
tk.Label(main, text="Welcome to Fin-Tracker").pack()
createMenu(main, userID)
main.mainloop()

