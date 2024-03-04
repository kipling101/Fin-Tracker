import datetime; from datetime import timedelta, datetime
import mysql.connector
import tkinter as tk
from tkinter import messagebox; from tkinter import ttk; from tkinter import Entry; from tkinter import tix; from tkinter.tix import Balloon
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
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
            tk.messagebox.showerror(title="Add Cash", message="Error: Entry Data.")
        except Exception as e:
            tk.messagebox.showerror(title="Add Cash", message="Error: " + str(e))
            
    def addDebt(userID, addDebtAmount, addDebtName, addDebtDate, addDebtAPR):
        try:
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
                
                duplicateCheck = "SELECT * FROM debtHoldings WHERE userID = %s AND debtName = %s and debtValue = %s and paymentDate = %s and APR = %s"
                cursor.execute(duplicateCheck, (userID, addDebtName, addDebtAmount, addDebtDate, addDebtAPR,))
                duplicate = cursor.fetchall()

                if duplicate:
                    modifyDebt = "UPDATE debtHoldings SET debtValue = debtValue + %s WHERE userID = %s AND debtName = %s and paymentDate = %s and APR = %s"
                    cursor.execute(modifyDebt, (addDebtAmount, userID, addDebtName, addDebtDate, addDebtAPR,))
                    db.commit(); tk.messagebox.showinfo("Success", "Debt added successfully!")
                    return
                
                #inserts the inputted data into the debtHoldings table
                addDebtSQL = "INSERT INTO debtHoldings (userID, debtValue, debtName, paymentDate, APR) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(addDebtSQL, (userID, addDebtAmount, addDebtName, addDebtDate, addDebtAPR,))
                db.commit()

            else: 
                tk.messagebox.showerror("Error", "Please fill in all fields!")
                return

            tk.messagebox.showinfo("Success", "Debt added successfully!")

        except mysql.connector.errors.DataError:
            tk.messagebox.showerror(title="Add Cash", message="Error: Entry Data.")
        except Exception as e:
            tk.messagebox.showerror(title="Add Cash", message="Error: " + str(e))
    
    def remDebt(userID, trnsNum, removeAmount):
        try:
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

        except mysql.connector.errors.DataError:
            tk.messagebox.showerror(title="Add Cash", message="Error: Entry Data.")
        except Exception as e:
            tk.messagebox.showerror(title="Add Cash", message="Error: " + str(e))

    try:
        cursor.execute("SELECT * FROM debtHoldings WHERE userID = %s", (userID,))
        curDebt = cursor.fetchall()

        main = tix.Tk()
        main.state('zoomed')
        main.title("FinTracker")
        #creates the menu interface
        menu.createMenu(main, userID)
    
        figSize = (4,4)

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


        #creates the information table
        breakLabel = tk.Label(main, text = "", font='Helvetica 16').pack()
        tree = ttk.Treeview(main)
        columns = ('Debt Value', 'Debt Name', 'APR', 'Transaction Number')  #column names

        #create columns
        tree['columns'] = columns

        for column in columns:
            tree.heading(column, text=column)
            tree.column(column, width=60)

        #adds only rows 1,2,4,5 to the table
        for i, row in enumerate(curDebt):
            tree.insert('', 'end', values=(row[1], row[2], row[4], row[5]))
        tree.column('#0', width=0)  #makes the first column v. small
        #adds the table to the window
        tree.pack()

        helpObject = Balloon(main)
        #creates interface which allows users to add or remove debt
        tk.Label(main, text = "Add Debt", font='Helvetica 16').place(x = 430, y = 600)

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

        helpObject.bind_widget(enterDebtName,balloonmsg="Enter the name of the debt.")
        helpObject.bind_widget(enterDebtAmount,balloonmsg="Enter the amount of debt on day 1, in £.")
        helpObject.bind_widget(enterDebtDate,balloonmsg="Enter the date the debt was taken out. Format: YYYY-MM-DD")
        helpObject.bind_widget(enterDebtAPR,balloonmsg="Enter the APR of the debt in percent. Do not include the % symbol.")
        helpObject.bind_widget(addDebtButton,balloonmsg="Add values entered to the debt table.")

        tk.Label(main, text = "Remove Debt", font='Helvetica 16').place(x = 1410, y = 600)

        debtSelLabel = tk.Label(main, text="Debt Transaction Number")
        debtSelLabel.place(x=1425, y=640)
        debtCombobox = ttk.Combobox(main, values=[debt[5] for debt in curDebt])
        debtCombobox.place(x=1455, y=670, width=100)
        
        removeAmountLabel = tk.Label(main, text="Amount to Remove")
        removeAmountLabel.place(x=1425, y=700)
        enterRemoveAmount = tk.Entry(main, width=35)
        enterRemoveAmount.place(x=1455, y=730, width=100)

        removeDebtButton = tk.Button(main, text="Remove Debt", command=lambda: remDebt(userID, debtCombobox.get(), enterRemoveAmount.get()))
        removeDebtButton.place(x=1420, y=780, width=100)

        helpObject.bind_widget(debtCombobox,balloonmsg="Select the transaction number of the debt you wish to remove.")
        helpObject.bind_widget(enterRemoveAmount,balloonmsg="Enter the amount of debt you wish to remove, in £.")
        helpObject.bind_widget(removeDebtButton,balloonmsg="Remove the debt from the table.")

        main.mainloop()

    except ValueError:
        tk.messagebox.showerror(title="Error", message="Error: Entry Data.")
    except Exception as e:
        tk.messagebox.showerror(title="Error", message="Error: " + str(e))