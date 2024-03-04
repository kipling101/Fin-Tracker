import tkinter as tk; from tkinter import ttk; from tkinter import *; from tkinter import messagebox
import mysql.connector

db = mysql.connector.connect(host ="localhost", user = "root", password = "pass123", db ="FinTracker")
cursor = db.cursor()

def loginSystem():

    global incorrectAttempts; incorrectAttempts = 0
    result = [False]
    def submitLogin():
        try:
            global incorrectAttempts
            nonlocal result
            inputUsername = enterUsrn.get()
            inputPassword = enterPwd.get()
            
            if inputUsername == "" and inputPassword == "":    
                tk.messagebox.showerror(title="Login",message="Please enter a username and password")

            #retrieves a list of users for which the username and password match the ones inputted into the Username and Password fields
            cursor.execute("SELECT * FROM Users WHERE name = %s and password = %s", (inputUsername, inputPassword))
            userPresent = cursor.fetchall()
        
            ## !! create code to handle multiple user with same name being returned !!
            if userPresent:
                #retrieves the privLevel of the user
                cursor.execute("SELECT privLevel FROM privileges WHERE userID = %s", (userPresent[0][0],))
                privResults = cursor.fetchall()
                tk.messagebox.showinfo(title="Login",message=" Login successful.\n\n Welcome "+inputUsername+".")
                result = [True, privResults, userPresent[0][0]]
                main.destroy()
            
            else:
                #if no users are returned the user will be informed via a error box
                tk.messagebox.showerror(title="Login",message="Incorrect username or password")
                incorrectAttempts += 1
                if incorrectAttempts == 3:
                    tk.messagebox.showerror(title="Login",message="Too many incorrect attempts, please try again later")
                    main.destroy()
                    result = [False]
                    
        except mysql.connector.errors.DataError:
            tk.messagebox.showerror(title="Add Cash", message="Error: Entry Data.")
        except Exception as e:
            tk.messagebox.showerror(title="Add Cash", message="Error: " + str(e))
    
    #creates the login window
    main = tk.Tk()
    main.geometry("250x300")
    main.title("FinTracker")
    main.resizable(0,0)
    
    labUsername = tk.Label(main, text ="Username")
    labUsername.place(x = 50, y = 20)

    enterUsrn = Entry(main, width = 35)
    enterUsrn.place(x = 75, y = 50, width = 100)

    labPwd = tk.Label(main, text ="Password")
    labPwd.place(x = 50, y = 80)

    enterPwd = Entry(main, show="*", width = 35)
    enterPwd.place(x = 75, y = 110, width = 100)
    #creates a button which calls the submitLogin function when clicked
    loginBtn = tk.Button(main, text ="Login", bg ='aqua', command = submitLogin)
    loginBtn.place(x = 150, y = 155, width = 55)

    cancelBtn = tk.Button(main, text ="Cancel", bg ='aqua', command = main.destroy)
    cancelBtn.place(x = 50, y = 155, width = 55)
    
    main.mainloop()

    return result