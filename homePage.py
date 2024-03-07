import tkinter as tk
import menu

def openHomePage(userID):
    #creates the home page
    main = tk.Tk()
    main.title("Fin-Tracker")
    main.state('zoomed')
    menu.createMenu(main, userID)

    homeLabel = tk.Label(main, text="Welcome to Fin-Tracker", font=("Arial", 24))
    homeLabel.pack()

    main.mainloop()