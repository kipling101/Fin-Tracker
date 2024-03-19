import tkinter as tk; from tkinter import Entry; from tkinter import messagebox
import homePage as hp; import cashForm as cf; import debtForm as df; import accountManagement as amf; import privCheck as pc; import investmentForm as inf

#each respective function checks the user has permission and then opens the page
def openHome(userID, main):
    main.destroy()
    hp.openHomePage(userID)

def openCash(userID, main):
    if pc.privCheck(userID, '01000') == False:
        tk.messagebox.showerror("Error", "You do not have permission to access this page.")
        return
    main.destroy()
    cf.openCashForm(userID)

def openDebt(userID, main):
    if pc.privCheck(userID, '10000') == False:
        tk.messagebox.showerror("Error", "You do not have permission to access this page.")
        return
    main.destroy()
    df.openDebtForm(userID)

def openAccount(userID, main):
    if pc.privCheck(userID, '00010') == False:
        tk.messagebox.showerror("Error", "You do not have permission to access this page.")
        return
    main.destroy()
    amf.openAccountMgmForm(userID)

def openInvestment(userID, main):
    if pc.privCheck(userID, '00100') == False:
        tk.messagebox.showerror("Error", "You do not have permission to access this page.")
        return
    main.destroy()
    inf.openInvestmentForm(userID)

def createMenu(main, userID): #creates the menu for the main window
    buttonFrame = tk.Frame(main)
    buttonFrame.pack(side="left")

    home = tk.Button(buttonFrame, text ="Home", font = "Helvetica 15", command = lambda: [openHome(userID, main)], width=20, height = 6)
    home.grid(row=0, sticky = "W")

    cash = tk.Button(buttonFrame, text ="Cash", font = "Helvetica 15", command = lambda: [openCash(userID, main)], width=20, height = 6)
    cash.grid(row=1, sticky = "W")

    debt = tk.Button(buttonFrame, text ="Debt", font = "Helvetica 15", command = lambda: [openDebt(userID, main)], width=20, height = 6)
    debt.grid(row=2, sticky = "W")

    investment = tk.Button(buttonFrame, text ="Investment", font = "Helvetica 15", command = lambda: [openInvestment(userID, main)], width=20, height = 6)
    investment.grid(row=3, sticky = "W")

    padding = tk.Label(buttonFrame, text = " ", width=20, height = 10)
    padding.grid(row=4, sticky = "W")

    account = tk.Button(buttonFrame, text ="Account", font = "Helvetica 15", command = lambda: [openAccount(userID, main)], width=20, height = 6)
    account.grid(row=5, sticky = "W")