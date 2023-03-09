# -*- coding: utf-8 -*-
"""
Simple Text Editor

Expanded version of the Codemy Tutorial:
https://www.youtube.com/watch?v=UlQRXJWUNBA 

Changelog: Strike function added.
"""

import os, sys
from tkinter import *
from tkinter import filedialog
from tkinter import font
from tkinter import messagebox
from tkinter import colorchooser
import win32print
import win32api

root = Tk()
root.title("Text Editor")
# root.iconbitmap('c:/path/to/icon.ico')
root.geometry("1200x680")

# Set variable for Open File name
global open_status_name
open_status_name = False

# Set variable for Paste text function
# Prevents error from occuring if Paste function doesn't find variable
global selected
selected = False


# Functions for the File Menu

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

# Print File Function
def print_file():
    # Detect default printer
    #print_name = win32print.GetDefaultPrinter()
    #status_bar.config(text=printer_name)

    # Request filename
    file_to_print = filedialog.askopenfilename(initialdir=os.path.dirname(__file__), title="Open File", filetypes=[("Text Files", "*.txt"), ("Python Files", "*.py"), ("HTML Files", "*.html"), ("All Files", "*.*")])    

    # If the command isn't canceled
    if file_to_print:
        win32api.ShellExecute(0, "print", file_to_print, None, ".", 0)

# Functions for the Edit Menu

# Cut Text
def cut_text(e):
    # The 'e' stands for event.  The function is listening for the key binding.
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

# Select All Text
def select_all(e):
    # Add sel tag to select all text
    my_text.tag_add('sel', '1.0', 'end')

# Clear All Text
def clear_all(e):
    my_text.delete(1.0, END)
    # Delete function doesn't require quotation marks

# Bold Text
def bold_it():
    # Check if any text is selected, otherwise app throws an error
    if my_text.tag_ranges("sel"):
        # Create the font
        bold_font = font.Font(my_text, my_text.cget("font"))
        bold_font.configure(weight="bold")
    
        # Configure a tag
        my_text.tag_configure("bold", font=bold_font)
    
        # Define Current tags
        current_tags = my_text.tag_names("sel.first")
    
        # If statement to see if tag has been set
        if "bold" in current_tags:
            #Unbold the selected text
            my_text.tag_remove("bold", "sel.first", "sel.last")
        else:
            my_text.tag_add("bold", "sel.first", "sel.last")
    else:
        # print("There is no selected text.")
        # Alert user that no text has been selected
        status_bar.config(text="No text has been selected       ")
        messagebox.showinfo("alert", "No text has been selected")        
        status_bar.config(text="Ready       ")

# Italics Text
def italics_it():
    # Check if any text is selected, otherwise app throws an error
    if my_text.tag_ranges("sel"):    
        # Create the font
        italics_font = font.Font(my_text, my_text.cget("font"))
        italics_font.configure(slant="italic")

        # Configure a tag
        my_text.tag_configure("italic", font=italics_font)

        # Define Current tags
        current_tags = my_text.tag_names("sel.first")

        # If statement to see if tag has been set
        if "italic" in current_tags:
            #Unitalicize the selected text
            my_text.tag_remove("italic", "sel.first", "sel.last")
        else:
            my_text.tag_add("italic", "sel.first", "sel.last")
    else:
        # Alert user that no text has been selected
        status_bar.config(text="No text has been selected       ")
        messagebox.showinfo("alert", "No text has been selected")        
        status_bar.config(text="Ready       ")

# Underline Text
def underline_it():
    # Check if any text is selected, otherwise app throws an error
    if my_text.tag_ranges("sel"):    
        # Create the font
        underline_font = font.Font(my_text, my_text.cget("font"))
        underline_font.configure(underline=True)

        # Configure a tag
        my_text.tag_configure("underline", font=underline_font)

        # Define Current tags
        current_tags = my_text.tag_names("sel.first")

        # If statement to see if tag has been set
        if "underline" in current_tags:
            #Underline the selected text
            my_text.tag_remove("underline", "sel.first", "sel.last")
        else:
            my_text.tag_add("underline", "sel.first", "sel.last")
    else:
        # Alert user that no text has been selected
        status_bar.config(text="No text has been selected       ")
        messagebox.showinfo("alert", "No text has been selected")        
        status_bar.config(text="Ready       ")

# Strike Text
def strike_it():
    # Check if any text is selected, otherwise app throws an error
    if my_text.tag_ranges("sel"):    
        # Create the font
        strike_font = font.Font(my_text, my_text.cget("font"))
        strike_font.configure(underline=True)

        # Configure a tag
        my_text.tag_configure("strike", font=strike_font)

        # Define Current tags
        current_tags = my_text.tag_names("sel.first")

        # If statement to see if tag has been set
        if "strike" in current_tags:
            #Underline the selected text
            my_text.tag_remove("strike", "sel.first", "sel.last")
        else:
            my_text.tag_add("strike", "sel.first", "sel.last")
    else:
        # Alert user that no text has been selected
        status_bar.config(text="No text has been selected       ")
        messagebox.showinfo("alert", "No text has been selected")        
        status_bar.config(text="Ready       ")

# Change Selected Text Color
def text_color():
    # Pick a color
    my_color = colorchooser.askcolor()[1]
    if my_color:
        # status_bar.config(text=my_color)

        # Create text font
        color_font = font.Font(my_text, my_text.cget("font"))

        # Configure a tag
        my_text.tag_configure("colored", font=color_font, foreground=my_color)

        # Define Current tags
        current_tags = my_text.tag_names("sel.first")

        # If statement to see if tag has been set
        if "colored" in current_tags:
            #Unitalicize the selected text
            my_text.tag_remove("colored", "sel.first", "sel.last")
        else:
            my_text.tag_add("colored", "sel.first", "sel.last")

# Change BG Color
def bg_color():
    # Pick a color
    my_color = colorchooser.askcolor()[1]
    if my_color:
        my_text.config(bg=my_color)

# Change All Text Color
def all_text_color():
    # Pick a color
    my_color = colorchooser.askcolor()[1]
    if my_color:
        my_text.config(fg=my_color)

# Left Align Text
def left_align():
    # Check if any text is selected, otherwise app throws an error
    if my_text.tag_ranges("sel"):    
        # Justify the text alignment to the left
        # Configure a tag
        my_text.tag_configure("left", justify="left")

        # Define Current tags
        current_tags = my_text.tag_names("sel.first")

        # If statement to see if tag has been set
        # Unalign the selected text if there are already tags
        if "left" in current_tags:            
            my_text.tag_remove("left", "sel.first", "sel.last")
        elif "center" in current_tags:
            my_text.tag_remove("center", "sel.first", "sel.last")
        elif "right" in current_tags:
            my_text.tag_remove("right", "sel.first", "sel.last")
        else:
            my_text.tag_add("left", "sel.first", "sel.last")
    else:
        # Alert user that no text has been selected
        status_bar.config(text="No text has been selected       ")
        messagebox.showinfo("alert", "No text has been selected")        
        status_bar.config(text="Ready       ")

# Center Align Text
def center_align():
    # Check if any text is selected, otherwise app throws an error
    if my_text.tag_ranges("sel"):    
        # Justify the text alignment to the center
        # Configure a tag
        my_text.tag_configure("center", justify="center")

        # Define Current tags
        current_tags = my_text.tag_names("sel.first")

        # If statement to see if tag has been set
        # Unalign the selected text if there are already tags
        if "left" in current_tags:            
            my_text.tag_remove("left", "sel.first", "sel.last")
        elif "center" in current_tags:
            my_text.tag_remove("center", "sel.first", "sel.last")
        elif "right" in current_tags:
            my_text.tag_remove("right", "sel.first", "sel.last")
        else:
            my_text.tag_add("center", "sel.first", "sel.last")
    else:
        # Alert user that no text has been selected
        status_bar.config(text="No text has been selected       ")
        messagebox.showinfo("alert", "No text has been selected")        
        status_bar.config(text="Ready       ")

# Right Align Text
def right_align():
    # Check if any text is selected, otherwise app throws an error
    if my_text.tag_ranges("sel"):    
        # Justify the text alignment to the right
        # Configure a tag
        my_text.tag_configure("right", justify="right")

        # Define Current tags
        current_tags = my_text.tag_names("sel.first")

        # If statement to see if tag has been set
        # Unalign the selected text if there are already tags
        if "left" in current_tags:            
            my_text.tag_remove("left", "sel.first", "sel.last")
        elif "center" in current_tags:
            my_text.tag_remove("center", "sel.first", "sel.last")
        elif "right" in current_tags:
            my_text.tag_remove("right", "sel.first", "sel.last")
        else:
            my_text.tag_add("right", "sel.first", "sel.last")
    else:
        # Alert user that no text has been selected
        status_bar.config(text="No text has been selected       ")
        messagebox.showinfo("alert", "No text has been selected")        
        status_bar.config(text="Ready       ")

# Turn on Night Mode
def night_mode_on():
    main_color = "#000000"
    second_color = "#373737"
    text_color = "green"

    root.config(bg=main_color)
    status_bar.config(bg=main_color, fg=text_color)
    my_text.config(bg=second_color)
    toolbar_frame.config(bg=main_color)
    # Toolbar Buttons
    bold_button.config(bg=second_color, fg=text_color)
    italics_button.config(bg=second_color, fg=text_color)
    redo_button.config(bg=second_color, fg=text_color)
    undo_button.config(bg=second_color, fg=text_color)
    color_text_button.config(bg=second_color, fg=text_color)
    # File Menu Colors
    file_menu.config(bg=main_color, fg=text_color)
    edit_menu.config(bg=main_color, fg=text_color)
    color_menu.config(bg=main_color, fg=text_color)
    options_menu.config(bg=main_color, fg=text_color)

# Turn off Night Mode
def night_mode_off():
    main_color = "SystemButtonFace"
    second_color = "SystemButtonFace"
    text_color = "black"

    root.config(bg=main_color)
    status_bar.config(bg=main_color, fg=text_color)
    my_text.config(bg="white")      # Restore to basic white
    toolbar_frame.config(bg=main_color) 
    # Toolbar Buttons
    bold_button.config(bg=second_color, fg=text_color)
    italics_button.config(bg=second_color, fg=text_color)
    redo_button.config(bg=second_color, fg=text_color)
    undo_button.config(bg=second_color, fg=text_color)
    color_text_button.config(bg=second_color, fg=text_color)
    # File Menu Colors
    file_menu.config(bg=main_color, fg=text_color)
    edit_menu.config(bg=main_color, fg=text_color)
    color_menu.config(bg=main_color, fg=text_color)
    options_menu.config(bg=main_color, fg=text_color)

# Create a Toolbar frame
toolbar_frame = Frame(root)
toolbar_frame.pack(fill=X)

# Create Main Frame
my_frame = Frame(root)
my_frame.pack(pady=5)

# Create Vertical Scrollbar for the Text Box
text_scroll = Scrollbar(my_frame)
text_scroll.pack(side=RIGHT, fill=Y)

# Create Horizontal Scrollbar for the Text Box
horizontal_scroll = Scrollbar(my_frame, orient="horizontal")
horizontal_scroll.pack(side=BOTTOM, fill=X)

# Create Text Box
my_text = Text(my_frame, width=97, height=25, font=("Helvetica", 16), selectbackground="yellow", selectforeground="black", undo=True, xscrollcommand=horizontal_scroll.set, yscrollcommand=text_scroll.set, wrap="none")
my_text.pack()

# Configure Scrollbar
text_scroll.config(command=my_text.yview)
horizontal_scroll.config(command=my_text.xview)

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
file_menu.add_command(label="Print", command=print_file)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)

# Add Edit Menu
edit_menu = Menu(my_menu, tearoff=False)
my_menu.add_cascade(label="Edit", menu=edit_menu)
edit_menu.add_command(label="Cut", command=lambda: cut_text(False), accelerator="(Ctrl+X)")
edit_menu.add_command(label="Copy", command=lambda: copy_text(False), accelerator="(Ctrl+C)")
edit_menu.add_command(label="Paste      ", command=lambda: paste_text(False), accelerator="(Ctrl+V)")
edit_menu.add_separator()
edit_menu.add_command(label="Select All", command=lambda: select_all(False), accelerator="(Ctrl+A)")
edit_menu.add_command(label="Clear All", command=lambda: clear_all(False))
edit_menu.add_separator()
edit_menu.add_command(label="Undo", command=my_text.edit_undo, accelerator="(Ctrl+Z)")
edit_menu.add_command(label="Redo", command=my_text.edit_redo, accelerator="(Ctrl+Y)")

# Add Color Menu
color_menu = Menu(my_menu, tearoff=False)
my_menu.add_cascade(label="Colors", menu=color_menu)
color_menu.add_command(label="Selected Text", command=text_color)
color_menu.add_command(label="All Text", command=all_text_color)
color_menu.add_command(label="Background", command=bg_color)
color_menu.add_separator()

# Add Format Menu
format_menu = Menu(my_menu, tearoff=False)
my_menu.add_cascade(label="Format", menu=format_menu)
format_menu.add_command(label="Left Align", command=left_align)
format_menu.add_command(label="Center Align", command=center_align)
format_menu.add_command(label="Right Align", command=right_align)
format_menu.add_separator()

# Add Options Menu
options_menu = Menu(my_menu, tearoff=False)
my_menu.add_cascade(label="Options", menu=options_menu)
options_menu.add_command(label="Night Mode On", command=night_mode_on)
options_menu.add_command(label="Night Mode Off", command=night_mode_off)

# Add Status Bar to Bottom of App
status_bar = Label(root, text="Ready       ", anchor=E)
status_bar.pack(fill=X, side=BOTTOM, ipady=15)

# Main Menu Bindings
root.bind("<Alt-Key-F>", file_menu)
# Edit Bindings
root.bind("<Control-Key-C>", copy_text)
root.bind("<Control-Key-c>", copy_text)
root.bind("<Control-Key-X>", cut_text)
root.bind("<Control-Key-x>", cut_text)
root.bind("<Control-Key-V>", paste_text)
root.bind("<Control-Key-v>", paste_text)
# Select Bindings
root.bind('<Control-Key-A>', select_all)
root.bind('<Control-Key-a>', select_all)

# Bold Button
bold_button = Button(toolbar_frame, text="Bold", command=bold_it)
bold_button.grid(row=0, column=0, sticky=W, padx=5)
# Italics Button
italics_button = Button(toolbar_frame, text="Italics", command=italics_it)
italics_button.grid(row=0, column=1, sticky=W, padx=5)
# Underline Button
underline_button = Button(toolbar_frame, text="Underline", command=underline_it)
underline_button.grid(row=0, column=2, sticky=W, padx=5)
# Strike Button
strike_button = Button(toolbar_frame, text="Strike", command=strike_it)
strike_button.grid(row=0, column=3, sticky=W, padx=5)

# Undo Button
undo_button = Button(toolbar_frame, text="Undo", command=my_text.edit_undo)
undo_button.grid(row=0, column=4, sticky=W, padx=5)
# Redo Button
redo_button = Button(toolbar_frame, text="Redo", command=my_text.edit_redo)
redo_button.grid(row=0, column=5, sticky=W, padx=5)

# Text Color
color_text_button = Button(toolbar_frame, text="Text Color", command=text_color)
color_text_button.grid(row=0, column=6, sticky=W, padx=5)

root.mainloop()



"""
Possible improvements:
    Change behavior of Bold function to highlight all text if Bold button
    is pushed a second time while highlight text partially tagged.
    
    Improve print function
    
    Change out the Clear All function for Delete
    
    Add key bindings to the functions of the File Menu
    
    Find a way to preserve formatting for text during saves
    
    Add Clear All Formatting function
    
    Organize code into Classes?
    
    Number the lines, then make the visibility of the lines optional
    
    Make the visibility of the status bar optional
    
"""
