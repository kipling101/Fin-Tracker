import tkinter as tk
import mysql.connector
from tkinter import *
from tkinter import messagebox

#initialise variables, will be made inputs later
userID = 1
levelReq = 10

def privCheck(userID, levelReq):

    #initialise database connection
    db = mysql.connector.connect(host ="localhost", user = "root", password = "pass123", db ="FinTracker")
    cursor = db.cursor()
    #finds the privilege level of the user given by the userID
    cursor.execute("SELECT privLevel FROM privileges WHERE userID = %s", (userID,))
    userPriv = cursor.fetchall()
    #converts the privilege level and the required privilege level to lists of binary digits
    levelReqList = [*str(levelReq)]
    userPrivList = [*str(userPriv[0][0])]

    #checks if the user has sufficient privileges for each element in the list, if element 0 of both lists 
    #are equal to 1 then it returns True, if user has does not have permission
    #for an element, but levelReq is 1 then it returns False. Otherwise returns nothing

    for i in range(len(levelReqList)):
        if levelReqList[i] == '1':
            if userPrivList[i] == '1':
                print("User has sufficient privileges for element", i,".")
                
            else:
                print("User does not have sufficient privileges for element", i,".")
                
        else:
            print("Not applicable.")

#runs the function
privCheck(userID, levelReq)