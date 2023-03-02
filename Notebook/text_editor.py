# -*- coding: utf-8 -*-
"""
Text Editor

Created following a Codemy Tutorial
Source: Build A Text Editor - Python Tkinter GUI Tutorial 
https://www.youtube.com/watch?v=UlQRXJWUNBA
https://www.youtube.com/watch?v=w5Nd4O76tDw
https://www.youtube.com/watch?v=yG0fAUn2uB0
https://www.youtube.com/watch?v=rUgAC_Ssflw

Changelog: Added keyboard binding for Cut Function
"""

import os
from tkinter import *
from tkinter import filedialog
from tkinter import font
from tkinter import messagebox

root = Tk()
root.title("Text Editor")
# root.iconbitmap('c:/path/to/icon.ico')
root.geometry("1200x660")

# Set variable for Open File name
global open_status_name
open_status_name = False

# Set variable for Paste text function
# Prevents error from occuring if Paste function doesn't find variable
global selected
selected = False

# Create New File Function
def new_file():
    # Delete previous text
    my_text.delete("1.0", END)
    root.title("New File")
    status_bar.config(text="New File       ")
    
    # Set variable for Open File name
    global open_status_name
    open_status_name = False

# Open File Function
def open_file():
    # Delete previous text
    my_text.delete("1.0", END)

    # Request filename
    # text_file = filedialog.askopenfilename(initialdir="C:/", title="Open File", filetypes=[("Text Files", "*.txt"), ("Python Files", "*.py"), ("All Files", "*.*")])    
    # Use os.path.dirname(__file__) to find the current directory of the .py file
    # Use  os.getcwd() for the current working directory 
    text_file = filedialog.askopenfilename(initialdir=os.path.dirname(__file__), title="Open File", filetypes=[("Text Files", "*.txt"), ("Python Files", "*.py"), ("HTML Files", "*.html"), ("All Files", "*.*")])
    
    
    # Check if there is a file name
    if text_file:
        # Make filename global so we can access it later
        global open_status_name
        open_status_name = text_file
    
    # Update Status Bar
    name = text_file
    status_bar.config(text=f"{name}       ")
    name = name.replace(os.path.dirname(__file__), "")
    root.title(f"{name} - Text Editor")
    
    # Open the File
    text_file = open(text_file, 'r')
    stuff = text_file.read()
    # Add file to textbox
    my_text.insert(END, stuff)
    # Close the opened file
    text_file.close()

# Save As File Function
def save_as_file():
    # Use os.path.dirname(__file__) to find the current directory of the .py file
    text_file = filedialog.asksaveasfilename(defaultextension="*.*", initialdir=os.path.dirname(__file__), title="Save File", filetypes=[("Text Files", "*.txt"), ("Python Files", "*.py"), ("HTML Files", "*.html"), ("All Files", "*.*")])
    if text_file:
        # Update Status Bar
        name = text_file
        status_bar.config(text=f"{name}       ")
        name = name.replace(os.path.dirname(__file__), "")
        root.title(f"{name} - Text Editor")
        
        # Save the file
        text_file = open(text_file, "w")
        text_file.write(my_text.get(1.0, END))
        # Close the file
        text_file.close()

# Save File Function
def save_file():
    global open_status_name
    if open_status_name:
        # Save the file
        text_file = open(open_status_name, "w")
        text_file.write(my_text.get(1.0, END))
        # Close the file
        text_file.close()
        # Confirm that the file has been saved
        messagebox.showinfo("confirmation", "File Saved!")        
        status_bar.config(text=f"Saved: {open_status_name}       ")
    else:
        save_as_file()

# Cut Text
def cut_text(e):
    global selected
    # Check if keyboad shortcut was used
    if e:
        # If Cut is being invoked by keyboard, grab what's on the clipboard
        selected = root.clipboard_get()
    else:
        if my_text.selection_get():
            # Grab selected text from text box
            selected = my_text.selection_get()
            # Delete selected text from text box
            my_text.delete("sel.first", "sel.last")
            # Clear the Clipboard, then append text
            root.clipboard_clear()
            root.clipboard_append(selected)
    
# Copy Text
def copy_text(e):
    global selected
    # Check if keyboad shortcut was used
    if e:
        # If Copy is being invoked by keyboard, grab what's on the clipboard
        selected = root.clipboard_get()
        
    if my_text.selection_get():
        # Grab selected text from text box
        selected = my_text.selection_get()
        # Clear the Clipboard, then append text
        root.clipboard_clear()
        root.clipboard_append(selected)

# Paste Text
def paste_text(e):
    global selected 
    # Check if keyboad shortcut was used
    if e:
        # If Paste is being invoked by keyboard, grab what's on the clipboard
        selected = root.clipboard_get()
    else:        
        if selected:
            position = my_text.index(INSERT)
            my_text.insert(position, selected)

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

# Create Menu
my_menu = Menu(root)
root.config(menu=my_menu)

# Add File Menu
file_menu = Menu(my_menu, tearoff=False)
my_menu.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="New", command=new_file)
file_menu.add_command(label="Open", command=open_file)
file_menu.add_command(label="Save", command=save_file)
file_menu.add_command(label="Save As", command=save_as_file)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)

# Add Edit Menu
edit_menu = Menu(my_menu, tearoff=False)
my_menu.add_cascade(label="Edit", menu=edit_menu)
edit_menu.add_command(label="Cut         Ctrl+x", command=lambda: cut_text(False))
edit_menu.add_command(label="Copy      Ctrl+c", command=lambda: copy_text(False))
edit_menu.add_command(label="Paste      Ctrl+v", command=lambda: paste_text(False))
edit_menu.add_separator()
edit_menu.add_command(label="Undo") 
edit_menu.add_command(label="Redo") 

# Add Status Bar to Bottom of App
status_bar = Label(root, text="Ready       ", anchor=E)
status_bar.pack(fill=X, side=BOTTOM, ipady=5)

# Edit Bindings
root.bind("<Control-Key-c>", copy_text)
root.bind("<Control-Key-x>", cut_text)
root.bind("<Control-Key-v>", paste_text)

root.mainloop()

