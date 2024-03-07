import mysql.connector
import datetime; from datetime import timedelta; from datetime import datetime; from dateutil.relativedelta import relativedelta

db = mysql.connector.connect(host="localhost", user="root", password="pass123", db="FinTracker")
cursor = db.cursor()

def onStart(userID):
    #retrives all payment data from the payments table for the user given by the userID
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


