import yfinance as yf
import datetime; from datetime import timedelta, datetime
import mysql.connector
import pandas as pd
import tkinter as tk
from tkinter import *; from tkinter import ttk
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import loginSystem as ls; import homePage as hp; import cashForm as cf; import debtForm as df
import accountManagement as amf; import onStart as os; import privCheck as pc; import menu

db = mysql.connector.connect(host ="localhost", user = "root", password = "pass123", db ="FinTracker")
cursor = db.cursor()


def openHomePage(userID):
    #creates the home page
    main = tk.Tk()
    main.title("Fin-Tracker")
    main.state('zoomed')
    menu.createMenu(main, userID)

    homeLabel = tk.Label(main, text="Welcome to Fin-Tracker", font=("Arial", 24))
    homeLabel.pack()

    main.mainloop()