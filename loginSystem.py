import tkinter as tk; from tkinter import ttk; from tkinter import *; from tkinter import messagebox
import mysql.connector
import yfinance as yf
import datetime; from datetime import timedelta; from datetime import datetime; from dateutil.relativedelta import relativedelta
import matplotlib; import matplotlib.pyplot as plt; matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg; from matplotlib.figure import Figure

db = mysql.connector.connect(host ="localhost", user = "root", password = "pass123", db ="FinTracker")
cursor = db.cursor()

userID = 1

def privCheck(userID, levelReq):

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

def onStart(userID):
    cursor.execute("SELECT * FROM payments WHERE userid = %s", (userID,))
    payments = cursor.fetchall()
    
    cursor.execute("SELECT * FROM lastAccessed WHERE userid = %s", (userID,))
    lastAccessed = cursor.fetchall()

    if len(lastAccessed) == 0:
        cursor.execute("INSERT INTO lastAccessed (userid, date) VALUES (%s, %s)", (userID, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        db.commit()

        cursor.execute("SELECT * FROM lastAccessed WHERE userid = %s", (userID,))
        lastAccessed = cursor.fetchall()
        
    for i in range(len(payments)):
        if datetime.strptime(str(payments[i][2]), '%Y-%m-%d %H:%M:%S') < datetime.strptime(str(lastAccessed[0][0]), '%Y-%m-%d %H:%M:%S'):

            compoundVal = ((1+((payments[i][4]/100)/365))**((datetime.now() - datetime.strptime(str(payments[i][5]), '%Y-%m-%d %H:%M:%S')).days))

            cursor.execute("INSERT INTO cash (userID, trnsName, trnsAmount, trnsDate, trnsAPR) VALUES (%s, %s, %s, %s, %s)", 
                           (userID, "Interest", compoundVal, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 0))

            cursor.execute("UPDATE lastAccessed SET date = %s WHERE userid = %s", (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), userID))
            cursor.execute("UPDATE payments SET paymentDate = %s WHERE userid = %s and paymentID = %s", ((datetime.now().strftime('%Y-%m-%d %H:%M:%S')+relativedelta(months=+1)), userID, payments[i][4]))
            db.commit()

def loginSystem(userID):
    global incorrectAttempts; incorrectAttempts = 0

    def submitLogin():
        global incorrectAttempts

        inputUsername = enterUsrn.get()
        inputPassword = enterPwd.get()
        
        if inputUsername == "" and inputPassword == "":    
            tk.messagebox.showerror(title="Login",message="Please enter a username and password")

        #retrieves a list of users for which the username and password match the ones inputted into the Username and Password fields
        cursor.execute("SELECT * FROM Users WHERE name = %s and password = %s", (inputUsername, inputPassword))
        userPresent = cursor.fetchall()
    
        #create code to handle multiple user with same name being returned
        if userPresent:
            #retrieves the privLevel of the user
            cursor.execute("SELECT privLevel FROM privileges WHERE userID = %s", (userPresent[0][0],))
            privResults = cursor.fetchall()
            tk.messagebox.showinfo(title="Login",message=" Login successful.\n\n Welcome "+inputUsername+".")
            return [True, privResults, userPresent[0][0]]
        
        else:
            #if no users are returned the user will be informed via a error box
            tk.messagebox.showerror(title="Login",message="Incorrect username or password")
            incorrectAttempts += 1
            print(incorrectAttempts)
            if incorrectAttempts == 3:
                tk.messagebox.showerror(title="Login",message="Too many incorrect attempts, please try again later")
                root.destroy()
            return incorrectAttempts
    
    #creates the window
    root = tk.Tk()
    root.geometry("250x300")
    root.title("FinTracker")
    root.resizable(0,0)

    labUsername = tk.Label(root, text ="Username")
    labUsername.place(x = 50, y = 20)

    enterUsrn = Entry(root, width = 35)
    enterUsrn.place(x = 75, y = 50, width = 100)

    labPwd = tk.Label(root, text ="Password")
    labPwd.place(x = 50, y = 80)

    enterPwd = Entry(root, show="*", width = 35)
    enterPwd.place(x = 75, y = 110, width = 100)
    #creates a button which calls the submitLogin function when clicked
    loginBtn = tk.Button(root, text ="Login", bg ='aqua', command = submitLogin)
    loginBtn.place(x = 150, y = 155, width = 55)

    cancelBtn = tk.Button(root, text ="Cancel", bg ='aqua', command = root.destroy)
    cancelBtn.place(x = 50, y = 155, width = 55)

    #keeps the code running until the window is closed
    root.mainloop()


def openDebtForm(userID):
    totalDebt = 0

    if privCheck(userID, '10000') == False:
        tk.messagebox.showerror("Error", "You do not have permission to access this page.")
        return
    
    def calcDebt(userID, totalDebt):
        #retrieves current debt information for the user given by the userID
        cursor.execute("SELECT * FROM debtHoldings WHERE userID = %s", (userID,))
        curDebt = cursor.fetchall()
        try:
            today = datetime.today() #finds the current date

            for i in curDebt:
                #extracts the debt information from the tuple
                debtName = i[2] #to be used for the visual interface
            
                debtDate = datetime.strptime(i[3], '%Y-%m-%d') #formats the debt data to a datetime object
                daysSince = (today - debtDate).days #finds the number of days since the debt was taken out

                #calculates the interest accrued on the debt using compound interest formula, and adds it to the total debt
                totalDebt += float(i[1])*((1+((i[4]/100)/365))**daysSince)

            #adds the debt information to the list of debts
            curDebt.sort(key=lambda x: datetime.strptime(x[3], '%Y-%m-%d'))
            #gets todays date, as well as the final date
            startDate = datetime.strptime(curDebt[0][3], '%Y-%m-%d')
            endDate = datetime.today()

            runningTotalEveryDay = []; dateList = []

            #iterates over every day in the list, and calculates the total debt on that day
            currentDate = startDate
            while currentDate <= endDate:
                runningTotal = 0
                #checks to see if the day the debt was taken out is before the current date in the loop
                for i in range(len(curDebt)):
                    #only process debts for the input userID
                    if curDebt[i][0] == userID:
                        debtDate = datetime.strptime(curDebt[i][3], '%Y-%m-%d')
                        #only adds the code if the debt was taken out before the current date
                        if debtDate <= currentDate:
                            daysSince = (currentDate - debtDate).days
                            runningTotal += float(curDebt[i][1])*((1+((curDebt[i][4]/100)/365))**daysSince)
                runningTotalEveryDay.append(runningTotal)
                dateList.append(currentDate)
                currentDate += timedelta(days=1)

            return [runningTotalEveryDay, dateList]
        
        except ValueError:
            tk.messagebox.showerror("Error", "An error has occured, please try again.")

    def addDebt(userID, addDebtAmount, addDebtName, addDebtDate, addDebtAPR):

        if userID and addDebtAmount and addDebtName and addDebtDate and addDebtAPR:
            if addDebtDate > datetime.now().strftime('%Y-%m-%d'):
                tk.messagebox.showerror("Error", "Please enter a valid date!")
                return
            if float(addDebtAmount) < 0 and addDebtAmount.replace(".", "").isnotnumeric():
                tk.messagebox.showerror("Error", "Please enter a valid amount!")
                return
            if float(addDebtAPR) < 0:
                tk.messagebox.showerror("Error", "Please enter a valid APR!")
                return
            if len(addDebtName) < 2 or len(addDebtName) > 20:
                tk.messagebox.showerror("Error", "Please enter a valid name!")
                return
            
            #inserts the inputted data into the debtHoldings table
            addDebtSQL = "INSERT INTO debtHoldings (userID, debtValue, debtName, paymentDate, APR) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(addDebtSQL, (userID, addDebtAmount, addDebtName, addDebtDate, addDebtAPR,))
            db.commit()

        else: 
            tk.messagebox.showerror("Error", "Please fill in all fields!")

        tk.messagebox.showinfo("Success", "Debt added successfully!")

    def remDebt(userID, trnsNum, removeAmount):
        #checks if there is a debt that matches the inputted data
        cursor.execute("SELECT * FROM debtHoldings WHERE userID = %s AND transactionNumber = %s", (userID, trnsNum))
        debts = cursor.fetchall()

        for debt in debts:
            #calculates the current value of the debt with compound interest
            debtValue = float(debt[1])
            debtDate = datetime.strptime(debt[3], '%Y-%m-%d')
            APR = float(debt[4])
            daysSince = (datetime.now() - debtDate).days
            currentValue = debtValue * ((1 + (APR / 100 / 365)) ** daysSince)

            #calculates the new value of the debt after removing the specified amount
            newValue = currentValue - float(removeAmount)
            if newValue < 0:
                newValue = 0

            #updates the debt value in the database
            cursor.execute("UPDATE debtHoldings SET debtValue = %s WHERE userID = %s AND transactionNumber = %s", (newValue, userID, trnsNum))
            db.commit()  

        if debts:
            tk.messagebox.showinfo("Success", "Debt removed successfully!")
        else:    
            tk.messagebox.showerror("Error", "Debt not found!")

    cursor.execute("SELECT * FROM debtHoldings WHERE userID = %s", (userID,))
    curDebt = cursor.fetchall()

    main = tk.Tk()
    main.title("Debt")
    main.geometry("500x500")

    width, height = 100, 100

    #converts from px to inches
    figsize = 1,1

    #creates the window for the graph of a set size
    f = Figure(figsize=figsize, dpi=100)
    #adds a subplot to the window
    a = f.add_subplot(111)
    calcDebt = calcDebt(userID, totalDebt)
    #plots the data on the graph
    a.plot(calcDebt(userID,totalDebt)[1], calcDebt(userID,totalDebt)[0], ls = '-')

    a.set_title("Debt Amount")
    a.set_xlabel("Date")
    a.set_ylabel("Value (£)")

    #creates the canvas for the graph to be displayed on
    canvas1=FigureCanvasTkAgg(f,master=main)
    canvas1.draw()
    canvas1.get_tk_widget().pack()

    #creates the add debt function, with boxes
    tk.Label(main, text = "Add Debt", font='Helvetica 16').place(x = 20, y = 600)

    addDebtName = tk.Label(main, text="Name")
    addDebtName.place(x=50, y=640)
    enterDebtName = Entry(main, width=35)
    enterDebtName.place(x=75, y=670, width=100)

    addDebtAmount = tk.Label(main, text="Value")
    addDebtAmount.place(x=50, y=700)
    enterDebtAmount = Entry(main, width=35)
    enterDebtAmount.place(x=75, y=730, width=100)

    addDebtDate = tk.Label(main, text="Date")
    addDebtDate.place(x=50, y=760)
    enterDebtDate = Entry(main, width=35)
    enterDebtDate.place(x=75, y=790, width=100)

    addDebtAPR = tk.Label(main, text="APR")
    addDebtAPR.place(x=50, y=820)
    enterDebtAPR = Entry(main, width=35)
    enterDebtAPR.place(x=75, y=850, width=100)

    addDebtButton = tk.Button(main, text="Add Debt", command=lambda: addDebt(userID, enterDebtAmount.get(), enterDebtName.get(), enterDebtDate.get(), enterDebtAPR.get()))
    addDebtButton.place(x=75, y=880, width=100)

    tk.Label(main, text = "Remove Debt", font='Helvetica 16').place(x = 1000, y = 600)

    #creates an entry field for the user to input the amount they want ro remove
    enterRemoveAmount = tk.Entry(main, width=35)
    enterRemoveAmount.place(x=1000, y=700, width=100)
    #creates a dropdown box which contains the tranaction ids for the debts
    debtCombobox = ttk.Combobox(main, values=[debt[5] for debt in curDebt])
    debtCombobox.place(x=1000, y=650, width=100)
    #button which removes the debt
    removeDebtButton = tk.Button(main, text="Remove Debt", command=lambda: remDebt(userID, debtCombobox.get(), enterRemoveAmount.get())).place(x=1000, y=750, width=100)

    main.mainloop()

def openCashForm(userID):
        
    if privCheck(userID, '01000') == False:
        tk.messagebox.showerror("Error", "You do not have permission to access this page.")
        return

    def cashAdd(userID, inputName, inputAmount, inputDate, inputAPR):
        #performs input validation
        if inputDate > datetime.now().strftime('%Y-%m-%d') or inputDate == "":
            tk.messagebox.showerror(title="Add Cash", message="Error: Invalid Date.")
            return
        if inputName == "":
            tk.messagebox.showerror(title="Add Cash", message="Error: Invalid Name.")
            return
        if userID == "" or inputName == "" or inputAmount == "" or inputDate == "" or inputAPR == "":
            tk.messagebox.showerror(title="Add Cash", message="Error: Please input all fields.")
            return
        if inputAmount.replace(".", "").isnumeric() and inputAPR.replace(".", "").isnumeric():
            #inserts the inputted data into the cash table
            cursor.execute("INSERT INTO cash (userID, trnsName, trnsAmount, trnsDate, trnsAPR) VALUES (%s, %s, %s, %s, %s)", 
                    (userID, inputName, float(inputAmount), inputDate, inputAPR))
            db.commit()
            tk.messagebox.showinfo(title="Add Cash", message="Cash changed successfully!")
        else:
            tk.messagebox.showerror(title="Add Cash", message="Error: Invalid Amount or APR.")
            return

    def cashRemove(userID, removeName, removeAmount, removeAPR):
        #inverts the values to add the cash and apr
        if userID == "" or removeName == "" or removeAmount == "" or removeAPR == "":
            tk.messagebox.showerror(title="Remove Cash", message="Error: Please input all fields.")
            return
        if removeAmount.replace(".", "").isnumeric() or removeAPR.replace(".", "").isnumeric():
            removeAmount = float(removeAmount); removeAPR = float(removeAPR)
            removeAmount = removeAmount * -1
            removeDate = datetime.now().strftime('%Y-%m-%d')
            cashAdd(userID, removeName, removeAmount, removeDate, removeAPR)
        else: 
            tk.messagebox.showerror(title="Remove Cash", message="Error: Invalid Amount or APR.")
            return

    def calcCash(userID):
        dateList = []

        #retrieves current cash information for the user given by the userID
        cursor.execute("SELECT * FROM cash WHERE userID = %s", (userID,))
        curCash = cursor.fetchall()

        #adds the cash information to the list of cash
        curCash.sort(key=lambda x: datetime.strptime(x[3], '%Y-%m-%d'))
        #get todays date, as well as the final date
        startDate = datetime.strptime(curCash[0][3], '%Y-%m-%d')
        endDate = datetime.today()

        runningTotalEveryDay = []
        dateList = []

        #iterates over every day in the list, and calculates the total cash on that day
        currentDate = startDate
        while currentDate <= endDate:
            runningTotal = 0
            #checks to see if the day the cash was taken out is before the current date in the loop
            for i in range(len(curCash)):
                #only process cash for the input userID
                if curCash[i][0] == userID:
                    cashDate = datetime.strptime(curCash[i][3], '%Y-%m-%d')
                    #only adds the code if the cash was taken out before the current date
                    if cashDate <= currentDate:
                        daysSince = (currentDate - cashDate).days
                        runningTotal += float(curCash[i][2]) * ((1 + ((float(curCash[i][4]) / 100) / 365)) ** daysSince)
            runningTotalEveryDay.append(runningTotal)
            dateList.append(currentDate)
            currentDate += timedelta(days=1)

        return [runningTotalEveryDay, dateList]

    #append to a 2d array, then plot the array
    main = tk.Tk()
    main.title("Cash")
    main.geometry("500x500")  # Set your desired width and height

    width, height = 300, 300

    #converts from px to inches
    figsize = (3, 3)

    #creates the window for the graph of a set size
    f = Figure(figsize=figsize, dpi=100)
    #adds a subplot to the window
    a = f.add_subplot(111)

    #plots the data on the graph
    cashData = calcCash(userID)
    a.plot(cashData[1], cashData[0], ls='-')
    a.set_title("Value")
    a.set_xlabel("Date")

    #creates the canvas for the graph to be displayed on
    canvas = FigureCanvasTkAgg(f, master=main)
    canvas.draw()
    canvas.get_tk_widget().pack()

    cursor.execute("SELECT * FROM cash WHERE userID = %s", (userID,))
    curCash = cursor.fetchall()

    #creates the add cash function, with boxes
    tk.Label(main, text="Add Cash", font='Helvetica 16').place(x=20, y=600)
    #creates the add cash function, with boxes
    addCashName = tk.Label(main, text="Name")
    addCashName.place(x=50, y=640)
    enterCashName = Entry(main, width=35)
    enterCashName.place(x=75, y=670, width=100)

    addCashAmount = tk.Label(main, text="Value")
    addCashAmount.place(x=50, y=700)
    enterCashAmount = Entry(main, width=35)
    enterCashAmount.place(x=75, y=730, width=100)

    addCashDate = tk.Label(main, text="Date")
    addCashDate.place(x=50, y=760)
    enterCashDate = Entry(main, width=35)
    enterCashDate.place(x=75, y=790, width=100)

    addCashAPR = tk.Label(main, text="APR")
    addCashAPR.place(x=50, y=820)
    enterCashAPR = Entry(main, width=35)
    enterCashAPR.place(x=75, y=850, width=100)
    #button which adds the cash
    addCashButton = tk.Button(main, text="Add Cash", command=lambda: cashAdd(userID, enterCashName.get(), enterCashAmount.get(), enterCashDate.get(), 
                                                                            enterCashAPR.get()))
    addCashButton.place(x=75, y=880, width=100)

    tk.Label(main, text = "Remove Cash", font='Helvetica 16').place(x = 1000, y = 600)

    #creates the remove cash function, with boxes
    removeCashName = tk.Label(main, text="Name")
    removeCashName.place(x=1000, y=640)
    enterRemoveCashName = Entry(main, width=35)
    enterRemoveCashName.place(x=1025, y=670, width=100)

    removeCashAmount = tk.Label(main, text="Value")
    removeCashAmount.place(x=1000, y=700)
    enterRemoveCashAmount = Entry(main, width=35)
    enterRemoveCashAmount.place(x=1025, y=730, width=100)

    removeCashAPR = tk.Label(main, text="APR")
    removeCashAPR.place(x=1000, y=780)
    enterRemoveCashAPR = Entry(main, width=35)
    enterRemoveCashAPR.place(x=1025, y=810, width=100)

    #button which removes the cash
    removeCashButton = tk.Button(main, text="Remove Cash", command=lambda: cashRemove(userID, enterRemoveCashName.get(), 
                                                                                    enterRemoveCashAmount.get(), enterRemoveCashAPR.get()))
    removeCashButton.place(x=1000, y=840, width=100)

    main.mainloop()

def openAccountCreator():
    #ensures that the user has permission to both access the admin page and create an account
    if privCheck(userID, '00011') == False:
        tk.messagebox.showerror("Error", "You do not have permission to access this page.")
        return
    
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

def accountManagementForm():

    if privCheck(userID, '00010') == False:
        tk.messagebox.showerror("Error", "You do not have permission to access this page.")
        return

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

    def menuPage():
        home = tk.Button(main, text ="Home", command = openHomePage(userID), width=25, height = 10).grid(row=0, sticky = "W")
        cash = tk.Button(main, text ="Cash", command = openCashForm(userID), width=25, height = 10).grid(row=1, sticky = "W")
        debt = tk.Button(main, text ="Debt", command = openDebtForm(userID), width=25, height = 10).grid(row=2, sticky = "W")
        account = tk.Button(main, text ="Account", command = accountManagementForm(userID), width=25, height = 14).grid(row=4, sticky = "W")

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

    menuPage()

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


def openInvestmentForm(userID):
    
    if privCheck(userID, '00100') == False:
        tk.messagebox.showerror("Error", "You do not have permission to access this page.")
        return
    
    def addInvestment(userID, addStockTicker, addShareNum, addShareDate):

        if addShareDate > datetime.now().strftime('%Y-%m-%d') or addShareDate == "":
            tk.messagebox.showerror(title="Add Investment", message="Error: Invalid Date.")
            return
        if float(addShareNum) <= 0:
            tk.messagebox.showerror(title="Add Investment", message="Error: Invalid Number of Shares.")
            return
        if addStockTicker == "":
            tk.messagebox.showerror(title="Add Investment", message="Error: Invalid Stock Ticker.")
            return
        #inserts the inputted data into the currInvestment table
        addInvSQL = "INSERT INTO currInvestment (userID, stockTicker, numSharesHeld, shareDate) VALUES (%s, %s, %s, %s)"
        cursor.execute(addInvSQL, (userID, addStockTicker, addShareNum, addShareDate))
        db.commit()

        tk.messagebox.showinfo("Success", "Investment added successfully!")

    def remInvestment(userID, remStockTicker, remShareNum):

        #checks if there is a investment that matches the inputted data
        remInvSQL = "SELECT * FROM currInvestment WHERE userID = %s AND stockTicker = %s"
        cursor.execute(remInvSQL, (userID, remStockTicker,))
        results = cursor.fetchall()

        #if a result is returned, deletes the investment from the database
        if results and results[2] >= remShareNum:
            newShareNum = remShareNum * -1
            
            removeInvSQL = "INSERT INTO currInvestment (userID, stockTicker, numSharesHeld, shareDate) VALUES (%s, %s, %s, %s)"
            cursor.execute(removeInvSQL, (userID, remStockTicker, float(newShareNum), datetime.now().strftime('%Y-%m-%d'),))
            db.commit()

            tk.messagebox.showinfo("Success", "Investment removed successfully!")
        else:    
            tk.messagebox.showerror("Error", "Investment not found!")

    def calcInvestment(userID):

        #finds all of the investment information for the user given by the userID
        calcInvSQL = "SELECT * FROM currInvestment WHERE userID = %s"
        cursor.execute(calcInvSQL, (userID,))
        curHolding = cursor.fetchall() #returns all the rows

        for i in curHolding:
            #for each investment, finds the current price and the initial price
            stockTicker = i[1]
            sharesHeld = i[2]
            datePur = i[3]
            
            currentDate = datetime.now().strftime('%Y-%m-%d') #finds the current date
            stockInfo = yf.Ticker(stockTicker) #sets the ticket to a given variable
            #finds the daily stock history information from the date of purchase to the current date
            stockHist = stockInfo.history(start=datePur, end=currentDate, interval = '1d')
        
            #fetch all investments for the current holding from the SQL table
            cursor.execute("SELECT * FROM currInvestment WHERE stockTrnsID = %s", (i[4],))
            investments = cursor.fetchall()
            
            valHistory = []
            dateHistory = []

            #iterate over each day
            for date, row in stockHist.iterrows():
                totalValue = 0

                #iterate over each holding
                for i in curHolding:
                    #fetch all investments for the current holding from the SQL table
                    cursor.execute("SELECT * FROM currinvestment WHERE stockTrnsID = %s AND shareDate <= %s", (i[4], date))
                    investments = cursor.fetchall()

                    #iterate over each investment
                    for investment in investments:
                        # Extract the number of shares and the opening price
                        sharesHeld = float(investment[2])  # replace 1 with the correct index for sharesHeld in your data
                        openPrice = stockHist['Open'][date]

                        #calculate teh value of this investment and add it to the total
                        totalValue += openPrice * sharesHeld

                #append the total value and the date to the lists
                valHistory.append(totalValue)
                dateHistory.append(date.strftime('%Y-%m-%d'))

            return [valHistory, dateHistory]

    main = tk.Tk()
    main.title("Cash")
    main.geometry("500x500")  # Set your desired width and height

    width, height = 300, 300

    #converts from px to inches
    figsize = (3, 3)

    #creates the window for the graph of a set size
    f = Figure(figsize=figsize, dpi=100)
    #adds a subplot to the window
    a = f.add_subplot(111)

    #plots the data on the graph
    investOverTime = calcInvestment(userID)
    a.plot(investOverTime[1], investOverTime[0], ls='-')
    a.set_title("Value")
    a.set_xlabel("Date")

    #creates the canvas for the graph to be displayed on
    canvas = FigureCanvasTkAgg(f, master=main)
    canvas.draw()
    canvas.get_tk_widget().pack()

    #creates the add cash function, with boxes
    tk.Label(main, text="Add Investment", font='Helvetica 16').place(x=20, y=600)
    #creates the add cash function, with boxes
    addTicker = tk.Label(main, text="Ticker")
    addTicker.place(x=50, y=640)
    enterTickerName = Entry(main, width=35)
    enterTickerName.place(x=75, y=670, width=100)

    addStockAmount = tk.Label(main, text="Quantity to Add")
    addStockAmount.place(x=50, y=700)
    enterStockAmount = Entry(main, width=35)
    enterStockAmount.place(x=75, y=730, width=100)

    addStockDate = tk.Label(main, text="Date")
    addStockDate.place(x=50, y=760)
    enterStockDate = Entry(main, width=35)
    enterStockDate.place(x=75, y=790, width=100)

    #button which adds the investment
    addInvestButton = tk.Button(main, text="Add Investment", command=lambda: addInvestment(userID, enterTickerName.get(), enterStockAmount.get(), 
                                                                                        enterStockDate.get()))
    addInvestButton.place(x=75, y=880, width=100)

    tk.Label(main, text = "Liquidate Position", font='Helvetica 16').place(x = 1000, y = 600)

    #creates the remove cash function, with boxes
    removeStockQuan = tk.Label(main, text="Quantity to Remove")
    removeStockQuan.place(x=1000, y=700)
    enterRemoveStockQuan = Entry(main, width=35)
    enterRemoveStockQuan.place(x=1025, y=730, width=100)

    cursor.execute("SELECT * FROM currInvestment WHERE userID = %s", (userID,))
    curInvestment = cursor.fetchall()

    #creates a dropdown box which contains the tranaction ids for the debts
    investCombobox = ttk.Combobox(main, values=[investment[1] for investment in curInvestment])
    investCombobox.place(x=1025, y=650, width=100)
    #button which removes the debt
    removeDebtButton = tk.Button(main, text="Liquidate Position", command=lambda: remInvestment(userID, investCombobox.get(), 
                                                                                                float(enterRemoveStockQuan.get()))).place(x=1000, y=780, width=100)

    main.mainloop()

def openHomePage(userID):
    print("Home Page")