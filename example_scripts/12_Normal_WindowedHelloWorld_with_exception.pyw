
from tkinter import *
root = Tk()
a = Label(root, text ="Hello World")
a.pack()
1/0  # without pyexewrap, this exception will make the window flash away mysteriously
root.mainloop()
