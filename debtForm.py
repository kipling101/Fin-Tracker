import datetime; from datetime import timedelta, datetime
import mysql.connector
import tkinter as tk; from tkinter import messagebox; from tkinter import Entry; from tkinter import ttk; from tkinter import tix; from tkinter.tix import Balloon
import matplotlib; matplotlib.use('TkAgg'); from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg; from matplotlib.figure import Figure
import menu

db = mysql.connector.connect(host ="localhost", user = "root", password = "pass123", db ="FinTracker")
cursor = db.cursor()

def openDebtForm(userID):
    totalDebt = 0
    
    def calcDebt(userID, totalDebt):
        try:
            #retrieves current debt information for the user given by the userID
            cursor.execute("SELECT * FROM debtHoldings WHERE userID = %s", (userID,))
            curDebt = cursor.fetchall()
    
            today = datetime.today() #finds the current date

            for i in curDebt:
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
                    #only process debts for the input userID, incase of SQL error
                    if curDebt[i][0] == userID:
                        debtDate = datetime.strptime(curDebt[i][3], '%Y-%m-%d')
                        #only adds the value if the debt was taken out before the current date
                        if debtDate <= currentDate:
                            daysSince = (currentDate - debtDate).days
                            runningTotal += float(curDebt[i][1])*((1+((curDebt[i][4]/100)/365))**daysSince)
                runningTotalEveryDay.append(runningTotal)
                dateList.append(currentDate)
                currentDate += timedelta(days=1)

            return [runningTotalEveryDay, dateList]
        except mysql.connector.errors.DataError:
            tk.messagebox.showerror(title="Error",message="Invalid data entered.")
        except Exception as e: 
            tk.messagebox.showerror(title="Error", message="Error: " + str(e))

    def addDebt(userID, addDebtAmount, addDebtName, addDebtDate, addDebtAPR):
        try:
            if userID and addDebtAmount and addDebtName and addDebtDate and addDebtAPR:
                if addDebtDate > datetime.now().strftime('%Y-%m-%d'):
                    tk.messagebox.showerror("Error", "Please enter a valid date!")
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
        except mysql.connector.errors.DataError:
            tk.messagebox.showerror(title="Error",message="Invalid data entered.")
        except Exception as e: 
            tk.messagebox.showerror(title="Error", message="Error: " + str(e))

    def remDebt(userID, removeName, removeAmount, removeAPR):
        try:
            #inverts the values of removeDebt amount
            if userID == "" or removeName == "" or removeAmount == "" or removeAPR == "":
                tk.messagebox.showerror(title="Remove Debt", message="Error: Please input all fields.")
                return
            if removeAmount.replace(".", "").isnumeric() or removeAPR.replace(".", "").isnumeric():
                removeAmount = float(removeAmount); removeAPR = float(removeAPR)
                removeAmount = removeAmount * -1
                removeDate = datetime.now().strftime('%Y-%m-%d')
                addDebt(userID, removeAmount, removeName, removeDate, removeAPR)
            else: 
                tk.messagebox.showerror(title="Remove Debt", message="Error: Invalid Amount or APR.")
                return
        except mysql.connector.errors.DataError:
            tk.messagebox.showerror(title="Error",message="Invalid data entered.")
        except Exception as e: 
            tk.messagebox.showerror(title="Error", message="Error: " + str(e))

    try:
        cursor.execute("SELECT * FROM debtHoldings WHERE userID = %s", (userID,))
        curDebt = cursor.fetchall()

        main = tix.Tk()
        main.state('zoomed')
        main.title("FinTracker")
        #creates the menu interface
        menu.createMenu(main, userID)

        figSize = 5.5, 4

        #code for creating the first graph which dispays debt over time
        f = Figure(figsize=figSize, dpi=100)
        debtOvTime = f.add_subplot(111)

        #plots the data on the graph
        calcDebt2 = calcDebt(userID, totalDebt)
        debtOvTime.plot(calcDebt2[1], calcDebt2[0], ls = '-')
        debtOvTime.set_title("Debt Amount")
        debtOvTime.set_xlabel("Date")
        debtOvTime.set_ylabel("Value (£)")

        #creates the canvas for the graph to be displayed on
        canvas1=FigureCanvasTkAgg(f,master=main)
        canvas1.draw()
        canvas1.get_tk_widget().pack()
        #creates interface which allows users to add or remove debt
        tk.Label(main, text = "Add Debt", font='Helvetica 16').place(x = 430, y = 600)

        #creates the information table
        breakLabel = tk.Label(main, text = "", font='Helvetica 16').pack() #creates a gap for aesthetics
        tree = ttk.Treeview(main)
        columns = ('Amount', 'Name', 'Date', 'APR', 'Transaction Number')  #column names

        #create columns
        tree['columns'] = columns

        for column in columns:
            tree.heading(column, text=column)
            tree.column(column, width=60)

        #adds only rows 1,2,4,5 to the table
        for i, row in enumerate(curDebt):
            tree.insert('', 'end', values=(row[1], row[2], row[3], row[4], row[5]))
        tree.column('#0', width=0)  #makes the first column v. small
        #adds the table to the window
        tree.pack()

        addDebtName = tk.Label(main, text="Name")
        addDebtName.place(x=445, y=640)
        enterDebtName = Entry(main, width=35)
        enterDebtName.place(x=470, y=670, width=100)

        addDebtAmount = tk.Label(main, text="Value")
        addDebtAmount.place(x=445, y=700)
        enterDebtAmount = Entry(main, width=35)
        enterDebtAmount.place(x=470, y=730, width=100)

        addDebtDate = tk.Label(main, text="Date")
        addDebtDate.place(x=445, y=760)
        enterDebtDate = Entry(main, width=35)
        enterDebtDate.place(x=470, y=790, width=100)

        addDebtAPR = tk.Label(main, text="APR")
        addDebtAPR.place(x=445, y=820)
        enterDebtAPR = Entry(main, width=35)
        enterDebtAPR.place(x=470, y=850, width=100)

        addDebtButton = tk.Button(main, text="Add Debt", command=lambda: addDebt(userID, enterDebtAmount.get(), enterDebtName.get(), enterDebtDate.get(), enterDebtAPR.get()))
        addDebtButton.place(x=440, y=900, width=100)

        tk.Label(main, text = "Remove Debt", font='Helvetica 16').place(x = 1410, y = 600)

         #creates the remove debt function, with boxes
        removeDebtName = tk.Label(main, text="Name")
        removeDebtName.place(x=1420, y=640)
        enterRemoveDebtName = Entry(main, width=35)
        enterRemoveDebtName.place(x=1455, y=670, width=100)

        removeDebtAmount = tk.Label(main, text="Value")
        removeDebtAmount.place(x=1420, y=700)
        enterRemoveDebtAmount = Entry(main, width=35)
        enterRemoveDebtAmount.place(x=1455, y=730, width=100)

        removeDebtAPR = tk.Label(main, text="APR")
        removeDebtAPR.place(x=1420, y=760)
        enterRemoveDebtAPR = Entry(main, width=35)
        enterRemoveDebtAPR.place(x=1455, y=790, width=100)

        #button which removes the debt
        removeDebtButton = tk.Button(main, text="Remove Debt", command=lambda: remDebt(userID, enterRemoveDebtName.get(), 
                                                                                        enterRemoveDebtAmount.get(), enterRemoveDebtAPR.get()))
        removeDebtButton.place(x=1420, y=840, width=100)

        helpObject = Balloon(main)

        helpObject.bind_widget(enterDebtName,balloonmsg="Enter the name of the debt.")
        helpObject.bind_widget(enterDebtAmount,balloonmsg="Enter the amount of debt on day 1, in £.")
        helpObject.bind_widget(enterDebtDate,balloonmsg="Enter the date the debt was taken out. Format: YYYY-MM-DD")
        helpObject.bind_widget(enterDebtAPR,balloonmsg="Enter the APR of the debt in percent. Do not include the % symbol.")
        helpObject.bind_widget(addDebtButton,balloonmsg="Add values entered to the debt table.")
        helpObject.bind_widget(enterRemoveDebtAmount,balloonmsg="Enter the amount of debt you wish to remove, in £.")
        helpObject.bind_widget(removeDebtButton,balloonmsg="Remove the debt from the table.")

        main.mainloop()

    except Exception as e: 
        tk.messagebox.showerror(title="Error", message="Error creating page: " + str(e))
