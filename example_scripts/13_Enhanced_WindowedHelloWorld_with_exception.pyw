#!/usr/bin/env python.exe -m pyexewrap
from tkinter import *
root = Tk()
a = Label(root, text ="Hello World")
a.pack()
1/0  # thanks to pyexewrap the traceback will be displayed to the user despite of the .pyw extension
root.mainloop()
