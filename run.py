import tkinter as tk
import mysql.connector
from tkinter import *
from tkinter import messagebox
from __main__ import *
import loginSystem; import cashForm; import debtForm; import privCheck; import investmentForm; import homePage; import accountManagement

#creates a menu interface
def goHome(userID, privLevel):
    if privCheck.__main__(userID, '00000') == True:
        print("HI")
        homePage.__main__(userID)

    else:
        tk.messagebox.showerror(title="Home",message="Insufficient privileges to access this page.")
        return False

def goCash():
    if privCheck.__main__(userID, '01000') == True:
        cashForm.__main__(userID)
    else:
        tk.messagebox.showerror(title="Cash",message="Insufficient privileges to access this page.")
        return False

def goDebt():
    if privCheck.__main__(userID, '10000') == True:
        debtForm.__main__(userID)
    else:
        tk.messagebox.showerror(title="Debt",message="Insufficient privileges to access this page.")
        return False

def goInvestment():
    if privCheck.__main__(userID, '00100') == True:
        investmentForm.__main__(userID)
    else:
        tk.messagebox.showerror(title="Investment",message="Insufficient privileges to access this page.")
        return False

def goAccount():
    if privCheck.__main__(userID, '00010') == True:
        accountManagement.__main__(userID)
    else:
        tk.messagebox.showerror(title="Account",message="Insufficient privileges to access this page.")
        return False

def goCreateAccount():
    if privCheck.__main__(userID, '00001') == True:
        import accountCreator
        accountCreator.__main__()
    else:
        tk.messagebox.showerror(title="Create Account",message="Insufficient privileges to access this page.")
        return False
    
loginList = loginSystem.__main__()
loginSystem.__main__.submitLogin()
privLevel = loginList[1]
userID = loginList[2]
if loginList[0] == True:
    print("Hi")
    goHome(userID, privLevel)

#for refereence 0 = debt, 1 = cash, 2 = investment, 3 = account management, 4 = create account
    