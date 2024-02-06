import tkinter as tk
import mysql.connector
from tkinter import *
from tkinter import messagebox

#initialises the database connection
db = mysql.connector.connect(host="localhost", user="root", password="pass123", db="FinTracker")
cursor = db.cursor()

def getUserPrivileges(userID):
    cursor.execute("SELECT privLevel FROM privileges WHERE userID = %s", (userID,))
    curUserPriv = cursor.fetchall()
    #returns the current user's privileges if they exist
    if curUserPriv:        
        return [*map(int, str(curUserPriv[0][0]))]
    #else, returns an error message and a default permission list of 00000
    tk.messagebox.showerror(title="Modify Permissions",message="Error fetching permissions, please try again later.")
    return [0, 0, 0, 0, 0]  #default value if fetching fails or user not found

#changes the variables to the current value of the user's permissions, called when the update button is pressed, used to update checkboxes
def changeVariable(var1, var2, var3, var4, var5):
    newPrivLevel = getUserPrivileges(userIDEntry.get()) #retrieves the current user's permissions level
    var1.set(newPrivLevel[0])
    var2.set(newPrivLevel[1])
    var3.set(newPrivLevel[2])
    var4.set(newPrivLevel[3])
    var5.set(newPrivLevel[4])

def permModify(userID, newPrivLevel):
    newPrivLevel = ''.join(map(str, newPrivLevel)) #converts the list of permissions to a string

    cursor.execute("SELECT privLevel FROM privileges WHERE userID = %s", (userID,))
    curUserPriv = cursor.fetchall()

    #verifies userID is present and exists
    if curUserPriv and userID:
        #sets the privilege level of the user, given by the userID, to the new privilege level
        cursor.execute("UPDATE privileges SET privLevel = %s WHERE userID = %s", (newPrivLevel, userID,))
        db.commit()
        #informs the user that the privilege level has been changed
        tk.messagebox.showinfo(title="Modify Permissions",message="Permissions modified successfully.")

    else: tk.messagebox.showerror(title="Modify Permissions",message="User ID not found.")

    userIDEntry.delete("0", "end")

#opens the account creation window
def openAccountCreator():
    import accountCreator
    accountCreator.main()

main = tk.Tk()
main.title("Modify Permissions")
main.state('zoomed')
#places locations for the tite, as well as the userID label and entry
title = tk.Label(main, text="Modify Permissions", font="Helvetica 20", justify="center")
title.place(x=350, y=20)

userIDLabel = tk.Label(main, text="User ID:", font="Helvetica 12")
userIDLabel.place(x=70, y=100)

userIDEntry = tk.Entry(main, font="Helvetica 12")
userIDEntry.place(x=170, y=100)

var1 = tk.IntVar(value=0)
var2 = tk.IntVar(value=0)
var3 = tk.IntVar(value=0)
var4 = tk.IntVar(value=0)
var5 = tk.IntVar(value=0)
#adds checkboxes which change the variable to the current value of the user's permissions
tk.Checkbutton(main, text="Cash", variable=var1).grid(row=1, sticky=tk.W)
tk.Checkbutton(main, text="Investment", variable=var2).grid(row=2, sticky=tk.W)
tk.Checkbutton(main, text="Debt", variable=var3).grid(row=3, sticky=tk.W)
tk.Checkbutton(main, text="Admin", variable=var4).grid(row=4, sticky=tk.W)
tk.Checkbutton(main, text="Account Creator", variable=var5).grid(row=5, sticky=tk.W)
#adds buttons which change the variable to the current value of the user's permissions
updateButton = tk.Button(main, text="Update", font="Helvetica 12", command=lambda: changeVariable(var1, var2, var3, var4, var5))
updateButton.place(x=300, y=190)

modifyButton = tk.Button(main, text="Modify", font="Helvetica 12", command=lambda: permModify(userIDEntry.get(), [var1.get(), var2.get(), 
                                                                                                                  var3.get(), var4.get(), var5.get()]))
modifyButton.place(x=150, y=190)

#places the button which opens the account creation window
openAccountCreatorButton = tk.Button(main, text="Create Account", font="Helvetica 12", command=lambda:openAccountCreator)
openAccountCreatorButton.place(x=450, y=190)

main.mainloop()