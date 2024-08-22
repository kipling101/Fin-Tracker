import loginSystem as ls; import onStart as os; import homePage as hp

#starts by opening the login page ***********
loginResult = ls.loginSystem()
if loginResult[0] != True:
    exit()
else: 
    userID = loginResult[2]
    os.onStart(userID)
    