import mysql.connector
import tkinter as tk
from tkinter import messagebox; from tkinter import Entry
import privCheck as pc

db = mysql.connector.connect(host ="localhost", user = "root", password = "pass123", db ="FinTracker")
cursor = db.cursor()

def openAccountCreator(userID):

    #ensures that the user has permission to both access the admin page and create an account
    if pc.privCheck(userID, '00011') == False:
        tk.messagebox.showerror("Error", "You do not have permission to access this page.")
        return
    
    def createAccount(inputUsername, inputPassword, inputPasswordVerify):
        try:
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
        except mysql.connector.errors.DataError:
            tk.messagebox.showerror(title="Add Cash", message="Error: Entry Data.")
        except Exception as e:
            tk.messagebox.showerror(title="Add Cash", message="Error: " + str(e))
        
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