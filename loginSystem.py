import tkinter as tk
import mysql.connector
from tkinter import *
from tkinter import messagebox

def submitLogin():

    inputUsername = enterUsername.get()
    inputPassword = enterPwd.get()
    print(inputUsername, inputPassword)
    
    if inputUsername == "" and inputPassword == "":    
        tk.messagebox.showerror(title="Login",message="Please enter a username and password")
    #initialises connection to database
    db = mysql.connector.connect(host ="localhost", user = "root", password = "pass123", db ="FinTracker")
    cursor = db.cursor()  

    #retrieves a list of users for which the username and password match the ones inputted into the Username and Password fields
    userList = "SELECT * FROM Users WHERE name = %s and password = %s"
    cursor.execute(userList, (inputUsername, inputPassword))
    results = cursor.fetchall()

    #add code to handle multiple user with same name being returned
    if results:
        #retrieves the privLevel of the user
        privCheck = "SELECT privLevel FROM privileges WHERE userID = %s"
        cursor.execute(privCheck, (results[0][0],))
        privResults = cursor.fetchall()
        tk.messagebox.showinfo(title="Login",message=" Login successful.\n\n Welcome "+inputUsername+".")
        return privResults

    else:
        #if no users are returned the user will be informed via a error box
        tk.messagebox.showerror(title="Login",message="Incorrect username or password")
        return False

#general code for creating a window                           
root = tk.Tk()
root.geometry("250x300")
root.title("FinTracker")
root.resizable(0,0)

labUsername = tk.Label(root, text ="Username")
labUsername.place(x = 50, y = 20)

enterUsername = Entry(root, width = 35)
enterUsername.place(x = 75, y = 50, width = 100)

labPwd = tk.Label(root, text ="Password")
labPwd.place(x = 50, y = 80)

enterPwd = Entry(root, show="*", width = 35)
enterPwd.place(x = 75, y = 110, width = 100)
#creates a button which calls the submitLogin function when clicked
loginBtn = tk.Button(root, text ="Login", bg ='aqua', command = submitLogin)
loginBtn.place(x = 150, y = 155, width = 55)

#keeps the code running until the window is closed
root.mainloop()