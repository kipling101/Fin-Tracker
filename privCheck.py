import mysql.connector
import tkinter as tk; from tkinter import messagebox

db = mysql.connector.connect(host ="localhost", user = "root", password = "pass123", db ="FinTracker")
cursor = db.cursor()

def privCheck(userID, levelReq):
    print(userID)
    #finds the privilege level of the user given by the userID
    cursor.execute("SELECT privLevel FROM privileges WHERE userID = %s", (userID,))
    userPriv = cursor.fetchall()
    #converts the privilege level and the required privilege level to lists of binary digits
    levelReqList = [*str(levelReq)]
    userPrivList = [*str(userPriv[0][0])]

    if userPriv == "":
        tk.messagebox.showerror("Error", "An error has occured, please try again.")
        return False

    if len(userPrivList) != 5:
        tk.messagebox.showerror("Error", "An error has occured, please try again.")
        return False
    
    #checks if the user has sufficient privileges for each element in the list, if element 0 of both lists 
    #are equal to 1 then it returns True, if user has does not have permission
    #for an element, but levelReq is 1 then it returns False. Otherwise returns nothing

    for i in range(len(levelReqList)):
        if levelReqList[i] == '1':
            if userPrivList[i] == '1':
                continue
            else:
                return False    
        else:
            continue
    
    return True