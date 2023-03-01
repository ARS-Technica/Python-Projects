# -*- coding: utf-8 -*-
"""
Text Editor

Created following a Codemy Tutorial

Source: Build A Text Editor - Python Tkinter GUI Tutorial #104
https://www.youtube.com/watch?v=UlQRXJWUNBA
"""

from tkinter import *
from tkinter import filedialog
from tkinter import font

root = Tk()
root.title('Text Editor')
# root.iconbitmap('c:/path/to/icon.ico')
root.geometry("1200x660")

# Create Main Frame
my_frame = Frame(root)
my_frame.pack(pady=5)

# Create Scrollbar for the Text Box
text_scroll = Scrollbar(my_frame)
text_scroll.pack(side=RIGHT, fill=Y)

# Create Text Box
my_text = Text(my_frame, width=97, height=25, font=("Helvetica", 16), selectbackground="yellow", selectforeground="black", undo=True, yscrollcommand=text_scroll.set)
my_text.pack()

# Configure Scrollbar
text_scroll.config(command=my_text.yview)




root.mainloop()
