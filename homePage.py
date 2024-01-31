import tkinter as tk

#general code for creating a window                           
root = tk.Tk()
root.geometry("250x300")
root.title("FinTracker")
root.resizable(0,0)

labUsername = tk.Label(root, text ="Username")
labUsername.place(x = 50, y = 20)

enterUsrn = Entry(root, width = 35)
enterUsrn.place(x = 75, y = 50, width = 100)

labPwd = tk.Label(root, text ="Password")
labPwd.place(x = 50, y = 80)

enterPwd = Entry(root, show="*", width = 35)
enterPwd.place(x = 75, y = 110, width = 100)
#creates a button which calls the submitLogin function when clicked
loginBtn = tk.Button(root, text ="Login", bg ='aqua', command = submitLogin)
loginBtn.place(x = 150, y = 155, width = 55)

#keeps the code running until the window is closed
root.mainloop()