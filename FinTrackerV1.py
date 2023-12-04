import numpy as np 
import pandas as pd
import yfinance as yf
from statistics import mean
import datetime; from datetime import timedelta, datetime
import mysql.connector
from mysql.connector import Error

addComm = False; finished = False; stockCheck = False; cashCheck = False; totValue = 0; accountType = "ISA"
#make sure the user can change the account type later

commands = ['Help','Stock','Cash','AddCommands']
whatCommands = ['Access a list of commands','Access stock commands','Access cash commands','Add commands to the list of commands']
moreInfo = ['This is a list of commands that can be used: \n\nhelp - provides a list of all available commands\n','This is a list of commands that can be used: \n\naddstock - adds a stock to the list of stocks \n\nvalue - calculates the value of all stocks in portfolio \n\ndividend - calculates the future dividends of the stocks\n', 'This is a list of commands that can be used: \n\naddcash - adds cash to the list of cash \nvalue - calculates the value of all cash in portfolio\n', 'This is a list of commands that can be used: \n\naddcommands - adds a command to the list of commands\n']

while True:
    try:

        toDo = str(input("What would you like to do? Type 'Help' for a list of commands")).lower()
        cashData = np.loadtxt("cashdata.csv", delimiter=',', dtype = object)
        stockData = np.loadtxt("stockdata.csv", delimiter=',', dtype = str)

        def calcValue(cashData,stockData,cashCheck,stockCheck):
        
            currentDate = datetime.now().strftime('%Y-%m-%d')
            currentDateComma = datetime.now().strftime('%Y,%m,%d')
            stockValue = float(0)
            cashValue = float(0)

            for stock in stockData:
                tickerInfo = yf.Ticker(stock[0])
                date1 = datetime.now() + timedelta(days=1); end = date1.strftime('%Y-%m-%d')
                tickerHis = tickerInfo.history(start=currentDate, end=end, interval = '1d')
                closing = tickerHis['Open'][0]
                stockValue = round(closing*float(stock[3])+stockValue,2)

            for data in cashData:
                timeDiff = datetime.now() - datetime(int(data[2]), int(data[3]), int(data[4]))
                cashValue = round(pow(1+(float(data[1])/100), timeDiff.days/365)*float(data[0])+cashValue,2)

            cashInput = np.concatenate((cashInput, currentDateComma,), axis=0)
            with open("cashdata.csv", 'a') as newCash:
                    np.savetxt(newCash, [cashInput], delimiter=',', fmt='%s')

            if cashCheck == True: 
                return cashValue
            elif stockCheck == True:
                return stockValue
            elif cashCheck == True and stockCheck == True:
                return stockValue + cashValue
                

        if "help" in toDo:
            print("\nThis is a list of commands that can be used: ")
            for i in range(len(commands)):
                print(commands[i], "-", whatCommands[i])
            helpExtra = str(input("\nType the name of a command to get extra information on it\n")).lower()
            for command in commands:
                if commands[command] == helpExtra:
                    print(moreInfo[command])


        elif "addcommands" in toDo:
            print("Adding command")
            while addComm == True:
                commandInp = str(input("What is the name of the command")); commands.append(commandInp)
                whatCommandsInp = str(input("What would you like the description to be?")); whatCommands.append(whatCommandsInp); print("Command added")
                addMore = str(input("Would you like to add another command? (Y/N)")).lower()   
                if addMore == "n": addComm = False; print("No more commands will be added, exiting"); break

        elif "stock" in toDo:
            stockCheck = True
            if "dividend" in toDo:
                print("Calculating dividend")
                for stock in stockData:
                    ticker = input(str("What is the ticker of the stock you would like to use?"))
                    datePriceInput = input(str("What day did you buy the stock?"))
                    tickerInfo = yf.Ticker(ticker)
                    date = datetime.datetime.strptime(datePriceInput, '%Y-%m-%d')
                    tickerHis = tickerInfo.history(start=date, interval = '1d')
                    dividend = tickerHis['Dividend'][0]
                    print("The dividend for", stock[0], "is", dividend)

            if "addstock" in toDo:
                print("Adding stock")
                
                while finished == False:  
                    ticker = input(str("What is the ticker of the stock you would like to add?"))
                    quantStock = input(str("How many stocks did you buy?"))
                    datePriceInput = input(str("What day did you buy the stock?")) 
        
                    date = datetime.datetime.strptime(datePriceInput, '%Y-%m-%d')
                    tickerInfo = yf.Ticker(ticker)
                    date1 = date + timedelta(days=1)
                    end = date1.strftime('%Y-%m-%d')
                    tickerHis = tickerInfo.history(start=date, end=end, interval = '1d')
                    opening = tickerHis['Open'][0]
                    wrArray = np.array([ticker, date, opening, quantStock])
                    with open("stockdata.csv", 'a') as newStock:
                        np.savetxt(newStock, [wrArray], delimiter=',', fmt='%s')

                    if str(input("Do you have anything else to add? Y/N")).lower() == "n": finished = True; break
                    elif str(input("Do you have anything else to add? Y/N")).lower() == "y": continue

            elif "value" in toDo:
                print("The value of your stocks is: £",calcValue(cashData,stockData,cashCheck,stockCheck))

        elif "cash" in toDo:
            cashCheck = True
            
            if "create" in toDo:
                print("Creating account. Current cash balance is: £",calcValue(cashData,stockData,cashCheck,stockCheck))
                
                cashInput = np.array([input("How much cash did you add?"),input("What is the APR?")],dtype=object)
                cashDate = np.array([input("What date did you add the cash? Please input in the form 'YYYY,MM,DD'")],dtype = object)
                cashInput = np.concatenate((cashInput, cashDate), axis=0); print(cashInput)
                with open("cashdata.csv", 'a') as newCash:
                    np.savetxt(newCash, [cashInput], delimiter=',', fmt='%s')
                print("Cash added") 

            elif "add" in toDo:
                print(cashData,"\nPlease note that the interest rate cannot be changed in this menu")
                accountNum = int(input("What account would you like to add to?"))
                cashAdd = float(input("How much cash would you like to add?"))
                for i in range(len(cashData)):
                    if cashData[i][0] == accountNum:
                        cashData[i][1] = cashData[i][1] + cashAdd 
                        print(cashData)
                        with open("cashdata.csv", 'a') as cashAppend:
                            np.savetxt(cashAppend, [cashData], delimiter=',', fmt='%s')

        elif "account" in toDo:
            print("The value of your portfolio is: £",calcValue(cashData,stockData,cashCheck,stockCheck), "\nThe type of account is", accountType)

    except ValueError:
        print("")


#To do list:
#1. Make it be able to calculate stock value at a certain time without the number being inputted by the user DONE
#2. Make it be able to calculate dividend paymemnts
#3. Finish cash section make it able to calculate interest into the future
#4. Make it able to add a certain amount of money at a repeated time
#5. Able to calculate taxes on dividens and income payments
#6. Input the type of portfolio that the user has. i.e. ISA, SIPP, etc.
#7. Add commands with command definitions later on
#8. Give it a web interface, maybe translate into JS to make it easier?
#9. Make it work with multiple users
#10. Make it able to calculate the value of a portfolio at a certain time
#11. Make it work down to the minute with the time in addstock section.
#12. Make it so that you can remove cash and stocks from the section

#np.append(cashData, [cashInput,intRate,cashDate]); print("Cash added")
