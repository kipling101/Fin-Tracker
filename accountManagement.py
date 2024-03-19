import mysql.connector
import tkinter as tk; from tkinter import Entry; from tkinter import messagebox; from tkinter import tix; from tkinter.tix import Balloon
import menu

db = mysql.connector.connect(host ="localhost", user = "root", password = "pass123", db ="FinTracker")
cursor = db.cursor()

def openAccountMgmForm(userID):

    def getUserPrivileges(userID):
        try:
            cursor.execute("SELECT privLevel FROM privileges WHERE userID = %s", (userID,))
            curUserPriv = cursor.fetchall()
            #returns the current user's privileges if they exist
            if curUserPriv:        
                return [*map(int, str(curUserPriv[0][0]))]
            #else, returns an error message and a default permission list of 00000
            tk.messagebox.showerror(title="Modify Permissions",message="Error fetching permissions, please try again later.")
            return [0, 0, 0, 0, 0]  #default value if fetching fails or user not found
        except mysql.connector.errors.DataError:
            tk.messagebox.showerror(title="Error",message="Error fetching permissions, please try again later.")
            return [0, 0, 0, 0, 0]  #default value if fetching fails or user not found
        except Exception as e: 
            tk.messagebox.showerror(title="Error", message="Error: " + str(e))
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
        try:
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
        except mysql.connector.errors.DataError:
            tk.messagebox.showerror(title="Error",message="Invalid data entered.")
        except Exception as e: 
            tk.messagebox.showerror(title="Error", message="Error: " + str(e))

    #opens the account creation window
    def openAccountCreator(userID):
        import accountCreator
        accountCreator.openAccountCreator(userID)

    main = tix.Tk()
    main.title("Modify Permissions")
    main.state('zoomed')

    def logOff():
        main.destroy()
        tk.messagebox.showinfo(title="Log Off", message="You have been logged off.")
        import loginSystem as ls
        ls.loginSystem()

    #creates the menu
    menu.createMenu(main, userID)
    #places locations for the tite, as well as the userID label and entry
    title = tk.Label(main, text="Modify Permissions", font="Helvetica 24", justify="center")
    title.place(x=340, y=20)

    userIDLabel = tk.Label(main, text="User ID:", font="Helvetica 12")
    userIDLabel.place(x=370, y=100)

    userIDEntry = tk.Entry(main, font="Helvetica 12", width=40)
    userIDEntry.place(x=460, y=100)

    var1 = tk.IntVar(value=0)
    var2 = tk.IntVar(value=0)
    var3 = tk.IntVar(value=0)
    var4 = tk.IntVar(value=0)
    var5 = tk.IntVar(value=0)
    #adds checkboxes which change the variable to the current value of the user's permissions
    tk.Checkbutton(main, text="Cash", variable=var1).place(x=370, y=180, anchor="w")
    tk.Checkbutton(main, text="Investment", variable=var2).place(x=370, y=210, anchor="w")
    tk.Checkbutton(main, text="Debt", variable=var3).place(x=370, y=240, anchor="w")
    tk.Checkbutton(main, text="Admin", variable=var4).place(x=370, y=270, anchor="w")
    tk.Checkbutton(main, text="Account Creator", variable=var5).place(x=370, y=300, anchor="w")
    #adds buttons which change the variable to the current value of the user's permissions
    modifyButton = tk.Button(main, text="Modify", font="Helvetica 12", command=lambda: permModify(userIDEntry.get(), [var1.get(), var2.get(), 
                                                                                                                    var3.get(), var4.get(), var5.get()]))
    modifyButton.place(x=340, y=360)

    updateButton = tk.Button(main, text="Update", font="Helvetica 12", command=lambda: changeVariable(var1, var2, var3, var4, var5))
    updateButton.place(x=500, y=360)

    #places the button which opens the account creation window
    openAccountCreatorButton = tk.Button(main, text="Create Account", font="Helvetica 12", command=lambda:openAccountCreator(userID))
    openAccountCreatorButton.place(x=660, y=360)

    logOffBtn = tk.Button(main, text="Log Off", font="Helvetica 12", bg="lightgrey", command=lambda: logOff())
    logOffBtn.place(x=428, y=450, width = 200)

    helpObject = Balloon(main)
    helpObject.bind_widget(modifyButton, balloonmsg="Modify the permissions of the user given by the User ID. Tick or untick the boxes to change the permissions.")
    helpObject.bind_widget(updateButton, balloonmsg="Update the permissions of the user given by the User ID. Press after inputting the userID.")
    helpObject.bind_widget(openAccountCreatorButton, balloonmsg="Open the account creation window.")
    helpObject.bind_widget(userIDEntry, balloonmsg="Input the User ID of the user whose permissions you want to modify.")

    main.mainloop()