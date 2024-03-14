import datetime; from datetime import timedelta, datetime
import mysql.connector
import tkinter as tk; from tkinter import messagebox; from tkinter import Entry; from tkinter import ttk; from tkinter import tix; from tkinter.tix import Balloon
import matplotlib; matplotlib.use('TkAgg'); from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg; from matplotlib.figure import Figure
import menu; import matplotlib.pyplot as plt

db = mysql.connector.connect(host ="localhost", user = "root", password = "pass123", db ="FinTracker")
cursor = db.cursor()

def openCashForm(userID):

    def cashAdd(userID, inputName, inputAmount, inputDate, inputAPR):
        try:
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
        except mysql.connector.errors.DataError:
            tk.messagebox.showerror(title="Add Cash", message="Error: Entry Data.")
        except Exception as e:
            tk.messagebox.showerror(title="Add Cash", message="Error: " + str(e))

    def cashRemove(userID, removeName, removeAmount, removeAPR):
        try:
            #inverts the values of the removeAmount value
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
        except mysql.connector.errors.DataError:
            tk.messagebox.showerror(title="Error",message="Invalid data entered.")
        except Exception as e: 
            tk.messagebox.showerror(title="Error", message="Error: " + str(e))

    def calcCash(userID):
        try:
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

            while startDate <= endDate:
                runningTotal = 0
                #checks to see if the day the cash was taken out is before the current date in the loop
                for i in range(len(curCash)):
                    cashDate = datetime.strptime(curCash[i][3], '%Y-%m-%d')
                    #only adds the code if the cash was taken out before the current date
                    if cashDate <= startDate:
                        daysSince = (startDate - cashDate).days
                        runningTotal += float(curCash[i][2]) * ((1 + ((float(curCash[i][4]) / 100) / 365)) ** daysSince)
                runningTotalEveryDay.append(runningTotal)
                dateList.append(startDate)
                startDate += timedelta(days=1)

            return [runningTotalEveryDay, dateList]
        except mysql.connector.errors.DataError:
            tk.messagebox.showerror(title="Error",message="Invalid data entered.")
        except Exception as e: 
            tk.messagebox.showerror(title="Error", message="Error: " + str(e))

    try:
        #append to a 2d array, then plot the array
        main = tix.Tk()
        main.title("Cash")
        main.state('zoomed')  #sets the size of the window
        #creates the menu
        menu.createMenu(main, userID)

        #converts from px to inches
        figsize = 5.5, 4

        #creates the window for the graph of a set size
        f = Figure(figsize=figsize, dpi=100)
        #adds a subplot to the window
        cashOvTime = f.add_subplot(111)

        #plots the data on the graph
        cashData = calcCash(userID)
        cashOvTime.plot(cashData[1], cashData[0], ls='-')
        cashOvTime.set_title("Total Value")
        cashOvTime.set_xlabel("Date")
        cashOvTime.set_ylabel("Value (£)")
        cashOvTime.set_facecolor('#F0F0F0')

        #creates the canvas for the graph to be displayed on
        canvas = FigureCanvasTkAgg(f, master=main)
        canvas.draw()
        canvas.get_tk_widget().pack()
        ## add something which lets users press a button to get a more detailed graph??? ##
        cursor.execute("SELECT * FROM cash WHERE userID = %s", (userID,))
        curCash = cursor.fetchall()

        #creates the information table
        breakLabel = tk.Label(main, text = "", font='Helvetica 16').pack() #creates a gap for aesthetics
        tree = ttk.Treeview(main)
        columns = ('Name', 'Amount', 'Date', 'APR', 'Transaction Number')  #column names

        #create columns
        tree['columns'] = columns

        for column in columns:
            tree.heading(column, text=column)
            tree.column(column, width=60)

        #adds only rows 1,2,4,5 to the table
        for i, row in enumerate(curCash):
            tree.insert('', 'end', values=(row[1], row[2], row[3], row[4], row[5]))
        tree.column('#0', width=0)  #makes the first column v. small
        #adds the table to the window
        tree.pack()

        #creates the add cash function, with boxes
        tk.Label(main, text="Add Cash", font='Helvetica 16').place(x=415, y=600)
    #
        addCashName = tk.Label(main, text="Name")
        addCashName.place(x=445, y=640)
        enterCashName = Entry(main, width=35)
        enterCashName.place(x=470, y=670, width=100)

        addCashAmount = tk.Label(main, text="Value")
        addCashAmount.place(x=445, y=700)
        enterCashAmount = Entry(main, width=35)
        enterCashAmount.place(x=470, y=730, width=100)

        addCashDate = tk.Label(main, text="Date")
        addCashDate.place(x=445, y=760)
        enterCashDate = Entry(main, width=35)
        enterCashDate.place(x=470, y=790, width=100)

        addCashAPR = tk.Label(main, text="APR")
        addCashAPR.place(x=445, y=820)
        enterCashAPR = Entry(main, width=35)
        enterCashAPR.place(x=470, y=850, width=100)
        #button which adds the cash
        addCashButton = tk.Button(main, text="Add Cash", command=lambda: cashAdd(userID, enterCashName.get(), enterCashAmount.get(), enterCashDate.get(), 
                                                                                enterCashAPR.get()))
        addCashButton.place(x=425, y=900, width=100)

        tk.Label(main, text = "Remove Cash", font='Helvetica 16').place(x = 1410, y = 600)

        #creates the remove cash function, with boxes
        removeCashName = tk.Label(main, text="Name")
        removeCashName.place(x=1420, y=640)
        enterRemoveCashName = Entry(main, width=35)
        enterRemoveCashName.place(x=1455, y=670, width=100)

        removeCashAmount = tk.Label(main, text="Value")
        removeCashAmount.place(x=1420, y=700)
        enterRemoveCashAmount = Entry(main, width=35)
        enterRemoveCashAmount.place(x=1455, y=730, width=100)

        removeCashAPR = tk.Label(main, text="APR")
        removeCashAPR.place(x=1420, y=760)
        enterRemoveCashAPR = Entry(main, width=35)
        enterRemoveCashAPR.place(x=1455, y=790, width=100)

        #button which removes the cash
        removeCashButton = tk.Button(main, text="Remove Cash", command=lambda: cashRemove(userID, enterRemoveCashName.get(), 
                                                                                        enterRemoveCashAmount.get(), enterRemoveCashAPR.get()))
        removeCashButton.place(x=1420, y=840, width=100)

        helpObject = Balloon(main)
        helpObject.bind_widget(enterCashName, balloonmsg="Name of the transaction.")
        helpObject.bind_widget(enterCashAmount, balloonmsg="Value of the transaction on the day it was entered, in £.")
        helpObject.bind_widget(enterCashDate, balloonmsg="Date of the transaction. Format: YYYY-MM-DD")
        helpObject.bind_widget(enterCashAPR, balloonmsg="Annual Percentage Rate of the transaction, do not include the % sign.")
        helpObject.bind_widget(addCashButton, balloonmsg="Press to add the transaction to the cash table.")
        helpObject.bind_widget(enterRemoveCashName, balloonmsg="Name of the transaction.")
        helpObject.bind_widget(enterRemoveCashAmount, balloonmsg="Value of the transaction on the day it was entered, in £.")
        helpObject.bind_widget(enterRemoveCashAPR, balloonmsg="Annual Percentage Rate of the transaction, do not include the % sign.")
        helpObject.bind_widget(removeCashButton, balloonmsg="Press to remove the transaction from the cash table.")

        main.mainloop()

    except Exception as e:
        tk.messagebox.showerror(title="Error", messahe="Error creating page: " + str(e))