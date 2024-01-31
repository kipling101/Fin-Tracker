import tkinter as tk
import mysql.connector
import tkinter as tk
from tkinter import *
from tkinter import messagebox

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

    #checks if the inputted password and the inputted password verification are the same, if they are 
    #then it inserts the username and password into the database
    if inputPassword == inputPasswordVerify:
        cursor.execute("INSERT INTO Users (name, password) VALUES (%s, %s)", (inputUsername, inputPassword))
        db.commit()

        userID = cursor.lastrowid
        #creates a new user in the privileges table with the default privileges of 00 and the userID from the Users table
        cursor.execute("INSERT INTO privileges (userID, privLevel) VALUES (%s, %s)", (userID, 00))
        db.commit()

        #informs the user that the account has been created
        tk.messagebox.showinfo(title="Create Account",message="Account created successfully.")
        main.destroy()

    else:
        print("Passwords do not match, please try again.")

main = tk.Tk()
main.geometry("400x600")
main.title("Create Account")
main.resizable(0,0)

title = tk.Label(main, text ="Create Account", font = "Helvetica 16", justify = "center")
title.place(x = 150, y = 20)

labUsername = tk.Label(main, text ="Username", justify = "center")
labUsername.place(x = 50, y = 85)

enterUsrn = Entry(main, width = 35, justify = "center")
enterUsrn.place(x=50, y = 110, width = 300)

labPwd = tk.Label(main, text ="Password", justify = "center")
labPwd.place(x = 50, y = 140)

enterPwd = Entry(main, show="*", width = 35)
enterPwd.place(x=50, y=160, width = 300)

labPwdVerify = tk.Label(main, text ="Verify Password", justify = "center")
labPwdVerify.place(x = 50, y = 190)

enterPwdVerify = Entry(main, show="*", width = 35, justify = "center")
enterPwdVerify.place(x=50, y=210, width = 300)

createBtn = tk.Button(main, text ="Create", bg ='aqua', command = lambda:createAccount(enterUsrn.get(), enterPwd.get(), enterPwdVerify.get()))
createBtn.place(x = 150, y = 250, width = 55)

cancelBtn = tk.Button(main, text ="Cancel", bg ='aqua', command = main.destroy)
cancelBtn.place(x = 50, y = 250, width = 55)

main.mainloop()

def goHome():
    print("home")
def goCash():
    print("cash")
def goDebt():
    print("debt")
def goAccount():
    print("account")

#creates the menu interface
root = tk.Tk()
root.geometry("1980x1080")
root.title("FinTracker")

home = tk.Button(root, text ="Home", command = goHome, width=25, height = 10).grid(row=0, sticky = "W")
cash = tk.Button(root, text ="Cash", command = goCash, width=25, height = 10).grid(row=1, sticky = "W")
debt = tk.Button(root, text ="Debt", command = goDebt, width=25, height = 10).grid(row=2, sticky = "W")
account = tk.Button(root, text ="Account", command = goAccount, width=25, height = 14).grid(row=4, sticky = "W")

root.mainloop()