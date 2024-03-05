import tkinter as tk; from tkinter import ttk; from tkinter import *; from tkinter import messagebox
import mysql.connector
import yfinance as yf
import datetime; from datetime import timedelta; from datetime import datetime; from dateutil.relativedelta import relativedelta
import matplotlib; import matplotlib.pyplot as plt; matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg; from matplotlib.figure import Figure
import loginSystem as ls; import homePage as hp; import cashForm as cf; import debtForm as df; import accountManagement as amf; import onStart as os; import privCheck as pc


#starts by opening the login page

#loginResult = ls.loginSystem()
loginResult = [True, 1]
if loginResult[0] != True:
    print("Exiting")
    exit()
else: 
    userID = loginResult[1]
    hp.openHomePage(userID)