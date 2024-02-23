import tkinter as tk; from tkinter import ttk; from tkinter import *; from tkinter import messagebox
import mysql.connector
import yfinance as yf
import datetime; from datetime import timedelta; from datetime import datetime; from dateutil.relativedelta import relativedelta
import matplotlib; import matplotlib.pyplot as plt; matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg; from matplotlib.figure import Figure

def menuPage():

    #creates the menu interface
    root = tk.Tk()
    root.geometry("1980x1080")
    root.title("FinTracker")

    home = tk.Button(root, text ="Home", command = lambda: print("Home"), width=25, height = 10).grid(row=0, sticky = "W")
    cash = tk.Button(root, text ="Cash", command = lambda: print("cash"), width=25, height = 10).grid(row=1, sticky = "W")
    debt = tk.Button(root, text ="Debt", command = lambda: print("debt"), width=25, height = 10).grid(row=2, sticky = "W")
    account = tk.Button(root, text ="Account", command = lambda: print("account"), width=25, height = 14).grid(row=4, sticky = "W")

    root.mainloop()

menuPage()