import loginSystem as ls; import homePage as hp

#starts by opening the login page

loginResult = ls.loginSystem()
if loginResult[0] != True:
    print("Exiting")
    exit()
else: 
    userID = loginResult[1]
    hp.openHomePage(userID)