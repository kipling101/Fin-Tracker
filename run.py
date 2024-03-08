import loginSystem as ls; import homePage as hp

#starts by opening the login page
#comment out as appropriate
#loginResult = ls.loginSystem()
loginResult = [True, 1]
if loginResult[0] != True:
    print("Exiting")
    exit()
else: 
    userID = loginResult[1]
    hp.openHomePage(userID)