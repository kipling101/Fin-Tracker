import tkinter as tk
import mysql.connector
from tkinter import *
from tkinter import messagebox
import datetime; from datetime import timedelta, datetime
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


userID = 1
totalDebt = 0
addDebtName = 'Credit Card'
addDebtAmount = 1000.0
addDebtDate = '2020-01-03'
addDebtAPR = 19.5

remDebtName = 'Credit Card'
remDebtAPR = 19.5

db = mysql.connector.connect(host ="localhost", user = "root", password = "pass123", db ="FinTracker")
cursor = db.cursor()

def calcDebt(userID,totalDebt):
    dateList =[]
    runningTotalList = []; runningTotalEveryDay = []
    runningTotal = 0
    #retrieves current debt information for the user given by the userID
    cursor.execute("SELECT * FROM debtHoldings WHERE userID = %s", (userID,))
    curDebt = cursor.fetchall()

    today = datetime.today() #finds the current date

    for i in curDebt:
        #extracts the debt information from the tuple
        debtName = i[2] #to be used for the visual interface
    
        debtDate = datetime.strptime(i[3], '%Y-%m-%d') #formats the debt data to a datetime object
        daysSince = (today - debtDate).days #finds the number of days since the debt was taken out

        #calculates the interest accrued on the debt using compound interest formula, and adds it to the total debt
        totalDebt += float(i[1])*((1+((i[4]/100)/365))**daysSince)

    #steps to create the value over time graph. find the number of days between the first and last debt, then create a for loop so that the value can be calculated for each date.
    
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
            debtDate = datetime.strptime(curDebt[i][3], '%Y-%m-%d')
            #only adds the code if the debt was taken out before the current date
            if debtDate <= currentDate:
                daysSince = (currentDate - debtDate).days
                runningTotal += float(curDebt[i][1]) * float(((1 + ((curDebt[i][4] / 100) / 365)) ** daysSince))

        runningTotalEveryDay.append(runningTotal)
        dateList.append(currentDate)
        #moves to the next day
        currentDate += timedelta(days=1)

    return [runningTotalEveryDay, dateList]

def addDebt(userID, addDebtAmount, addDebtName, addDebtDate, addDebtAPR):

    #inserts the inputted data into the debtHoldings table
    addDebtSQL = "INSERT INTO debtHoldings (userID, debtValue, debtName, paymentDate, APR) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(addDebtSQL, (userID, addDebtAmount, addDebtName, addDebtDate, addDebtAPR,))
    db.commit()

    print("Debt successfull added!")

def remDebt(userID, remDebtName, remDebtAPR):

    #checks if there is a debt that matches the inputted data
    cursor.execute("SELECT * FROM debtHoldings WHERE userID = %s AND debtName = %s AND APR = %s", (userID, remDebtName, remDebtAPR))
    presCheck = cursor.fetchall()

    #if a result is returned, deletes the debt from the database 
    if presCheck:
        cursor.execute("DELETE FROM debtHoldings WHERE userID = %s AND debtName = %s AND APR = %s", (userID, remDebtName, remDebtAPR,))
        db.commit()

        print("Debt removed successfully!")

    else:    
        print("No such debt exists, please verify data inputted and try again.")

calcDebt(userID,totalDebt)

main = tk.Tk()
main.title("Modify Permissions")
main.geometry("500x500")  # Set your desired width and height

# Create a Matplotlib figure and plot with the specified size
f = Figure(figsize=(5,5), dpi=100)
a = f.add_subplot(111)

a.plot(calcDebt(userID,totalDebt)[1], calcDebt(userID,totalDebt)[0], ls = '-')

a.set_title("Debt Amount")
a.set_xlabel("Date")
a.set_ylabel("Value (£)")

a.set_ylim(0)

canvas1=FigureCanvasTkAgg(f,master=main)
canvas1.draw()
canvas1.get_tk_widget().pack(side="top",fill='both',expand=True)

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

main.mainloop()