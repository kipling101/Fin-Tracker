import homePage as hp; import onStart as os

#starts by opening the login page

#loginResult = ls.loginSystem()
loginResult = [True, 1]
if loginResult[0] != True:
    print("Exiting")
    exit()
else: 
    userID = loginResult[1]
    os.onStart(userID)