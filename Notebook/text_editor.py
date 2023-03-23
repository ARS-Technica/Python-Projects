# -*- coding: utf-8 -*-
"""
Simple Text Editor

Expanded version of the Codemy Tutorial:
https://www.youtube.com/watch?v=UlQRXJWUNBA 

Changelog: Adding Line Numbering Function.  (Rough going.)
"""

import os, sys
from tkinter import *
from tkinter import filedialog
from tkinter import font
from tkinter import messagebox
from tkinter import colorchooser
import tkinter.ttk as ttk   # To toggle Status Bar visibility
import win32print
import win32api

root = Tk()
root.title("Text Editor")
# root.iconbitmap('c:/path/to/icon.ico')
root.geometry("1200x690")
root.resizable(True,True)


# ***************** Setting Global Variables ***************** #

# Set variable for Open File name
global open_status_name
open_status_name = False

# Set variable for Paste text function
# Prevents error from occuring if Paste function doesn't find variable
global selected
selected = False

# Set variable for Status Bar status
statusbar_is_on = IntVar()
# checkbutton = Checkbutton(root, text ="Test", variable=statusbar_is_on)
# checkbutton.select()


# ***************** Building the Interface ***************** #

# Create a Toolbar Frame
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
my_text = Text(my_frame, width=97, height=25, font=("Helvetica", 16),
               selectbackground="yellow", selectforeground="black", undo=True,
               xscrollcommand=horizontal_scroll.set, yscrollcommand=text_scroll.set, wrap="none")
my_text.pack(side="top", fill="both", expand=True)

# Former selectforeground="#999999"

"""
def highlight_current_line(interval=100):
    # Updates the 'current line' highlighting every "interval" milliseconds
    my_text.tag_remove("current_line", 1.0, "end")
    my_text.tag_add("current_line", "insert linestart", "insert lineend+1c")
    my_text.after(interval, highlight_current_line)

# Call highlight_current_line function to change the bg color on a rolling basis
highlight_current_line()
# Select the color of the Current Line
my_text.tag_configure("current_line", background="#e9e9e9") 
"""
  
# Configure Scrollbar
text_scroll.config(command=my_text.yview)
horizontal_scroll.config(command=my_text.xview)

# Add Status Bar to Bottom of App
status_bar = Label(root, text="Ready       ", anchor=E)
status_bar.pack(fill=X, side=BOTTOM, ipady=15)


# ***************** Functions for the File Menu ***************** #

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

# Close App Function
def exit_file():
    message = messagebox.askyesno(
        "Do you want to exit?",
        "Do you want to save the file? " )

    if message:
        save_as_file()
        # root.quit()
        root.destroy()
    else:
        # root.quit()
        root.destroy()


# ***************** Functions for the Edit Menu ***************** #

# Cut Text
def cut_text(e):
    # The 'e' stands for event.  The function is listening for the key binding.
    global selected
    # Check if keyboad shortcut was used
    if e:
        # If Cut is being invoked by keyboard, grab what's on the clipboard
        selected = root.clipboard_get()
    else:
        """
        Using Try/Except here rather than if/else avoids the following error,
        which results from attempting to use Cut without first selecting text.

        return self.tk.call(('selection', 'get') + self._options(kw))
_tkinter.TclError: PRIMARY selection doesn't exist or form "STRING" not defined
        """
        # if my_text.selection_get():
        try:
            # Grab selected text from text box
            selected = my_text.selection_get()
            # Delete selected text from text box
            my_text.delete("sel.first", "sel.last")
            # Clear the Clipboard, then append text
            root.clipboard_clear()
            root.clipboard_append(selected)
        except:
            # Alert user that no text has been selected
            status_bar.bell() # Windows bell sound
            status_bar.config(text="No text has been selected       ")
            # messagebox.showinfo("alert", "No text has been selected")        
            # status_bar.config(text="Ready       ")

# Copy Text
def copy_text(e):
    global selected
    # Check if keyboad shortcut was used
    if e:
        # If Copy is being invoked by keyboard, grab what's on the clipboard
        selected = root.clipboard_get()
    else:
        """
        Using Try/Except here rather than if/else avoids the following error,
        which results from attempting to use Copy without first selecting text.

        return self.tk.call(('selection', 'get') + self._options(kw))
_tkinter.TclError: PRIMARY selection doesn't exist or form "STRING" not defined
        """
        # if my_text.selection_get():
        try:
            # Grab selected text from text box
            selected = my_text.selection_get()
            # Clear the Clipboard, then append text
            root.clipboard_clear()
            root.clipboard_append(selected)
        except:
            # Alert user that no text has been selected
            status_bar.bell() # Windows bell sound
            status_bar.config(text="No text has been selected       ")
            # messagebox.showinfo("alert", "No text has been selected")        
            # status_bar.config(text="Ready       ")        

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

# Delete Selected Text
def delete_text(e):
    # Check if any text is selected, otherwise app throws an error
    if my_text.tag_ranges("sel"):
        # Delete selected text
        my_text.delete("sel.first", "sel.last")
    else:
        # Alert user that no text has been selected
        status_bar.bell() # Windows bell sound
        status_bar.config(text="No text has been selected       ")
        # messagebox.showinfo("alert", "No text has been selected")        
        # status_bar.config(text="Ready       ")             

# Copy All Text
def copy_all(e):
    pass

# Select All Text
def select_all(e):
    # Add sel tag to select all text
    my_text.tag_add('sel', '1.0', 'end')

# Clear All Text
def clear_all(e):
    my_text.delete(1.0, END)
    # Delete function doesn't require quotation marks


# ***************** Functions for the Search Menu ***************** #

# Search Text
def find():
    pass

def fuzzy_find():
    pass

def find_next():
    pass

def replace():
    pass

def go_to_line():
    pass


# ***************** Alignment Functions for the Format Menu ***************** #

# Removes Other Text Alignments
def remove_align():
    # Define Current tags
    current_tags = my_text.tag_names("sel.first") 
    # Unalign the selected text if there are already tags
    if "left" in current_tags:            
        my_text.tag_remove("left", "sel.first", "sel.last")
    if "right" in current_tags:
        my_text.tag_remove("right", "sel.first", "sel.last")
    if "center" in current_tags:
        my_text.tag_remove("center", "sel.first", "sel.last")

# Left Align Text
def left_align():
    # Check if any text is selected, otherwise app throws an error
    if my_text.tag_ranges("sel"):
        # Removes Other Text Alignments
        remove_align()
                
        # Justify the text alignment to the left
        # Configure a tag
        my_text.tag_configure("left", justify="left")

        my_text.tag_add("left", "sel.first", "sel.last")
    else:
        # Alert user that no text has been selected
        status_bar.bell() # Windows bell sound
        status_bar.config(text="No text has been selected       ")
        messagebox.showinfo("alert", "No text has been selected")        
        status_bar.config(text="Ready       ")

# Right Align Text
def right_align():
    # Check if any text is selected, otherwise app throws an error
    if my_text.tag_ranges("sel"):
        # Removes Other Text Alignments
        remove_align()

        # Justify the text alignment to the right
        # Configure a tag
        my_text.tag_configure("right", justify="right")

        my_text.tag_add("right", "sel.first", "sel.last")
    else:
        # Alert user that no text has been selected
        status_bar.bell() # Windows bell sound
        status_bar.config(text="No text has been selected       ")
        messagebox.showinfo("alert", "No text has been selected")        
        status_bar.config(text="Ready       ")

# Center Align Text
def center_align():
    # Check if any text is selected, otherwise app throws an error
    if my_text.tag_ranges("sel"):
        # Removes Other Text Alignments
        remove_align()
                
        # Justify the text alignment to the center
        # Configure a tag
        my_text.tag_configure("center", justify="center")

        my_text.tag_add("center", "sel.first", "sel.last")
    else:
        # Alert user that no text has been selected
        status_bar.bell() # Windows bell sound
        status_bar.config(text="No text has been selected       ")
        messagebox.showinfo("alert", "No text has been selected")        
        status_bar.config(text="Ready       ")

# Removes Other Text Alignments
def justify_align():
    # Check if any text is selected, otherwise app throws an error
    if my_text.tag_ranges("sel"):
        # Removes Other Text Alignments
        remove_align()
    else:
        # Alert user that no text has been selected
        status_bar.bell() # Windows bell sound
        status_bar.config(text="No text has been selected       ")
        messagebox.showinfo("alert", "No text has been selected")        
        status_bar.config(text="Ready       ")


# ***************** Color Functions for the Format Menu ***************** #

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


# ***************** Font Styling Functions for the Format Menu ***************** #

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
        strike_font.configure(overstrike=True)

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


# ***************** Functions for the Tools Menu ***************** #

# Tools for changing Cases
def case_tools():
    pass

# Tools for special Characters
def character_tools():
    pass

# Tools for evaluation Expressions
def expression_tools():
    pass

# Tools for sorting Lines of text
def line_tools():
    pass

# Tools for text Statistics
def statistic_tools():
    pass

# Tools for transforming Text
def transform_tools():
    pass

# Tools for altering White Space
def space_tools():
    pass


# ***************** Functions for the Options Menu ***************** #

highlight_enabled = False

# Toggle line highlighting on and off
def toggle_line_highlighting():
    if highlighting.get() == True:
        # Highlight the Current Line
        def highlight_current_line(interval=100):
            # Updates the 'current line' highlighting every "interval" milliseconds
            my_text.tag_remove("current_line", 1.0, "end")
            my_text.tag_add("current_line", "insert linestart", "insert lineend+1c")
            my_text.after(interval, highlight_current_line)
        
        # Call highlight_current_line function to change the bg color on a rolling basis
        highlight_current_line()
        # Select the color of the Current Line
        my_text.tag_configure("current_line", background="#e9e9e9", selectbackground="#999999") 

    else:
        global highlight_enabled
        highlight_enabled = False
        
        if night.get() == True:
            my_text.tag_remove("current_line", 1.0, "end")
            my_text.tag_configure("current_line", background="#373737", selectbackground="yellow")
            my_text.tag_add("current_line", 1.0, "end")
        else:
            my_text.tag_remove("current_line", 1.0, "end")
            my_text.tag_configure("current_line", background="white", selectbackground="yellow")
            my_text.tag_add("current_line", 1.0, "end")








# Toggle line numbering on and off
def create_text_line_numbers(canvas, text_widget):
    def redraw(*args):
        # Redraw line numbers
        canvas.delete("all")

        i = text_widget.index("@0,0")
        while True:
            dline = text_widget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = str(i).split(".")[0]
            canvas.create_text(2, y, anchor="nw", text=linenum)
            i = text_widget.index("%s+1line" % i)

    return redraw


def create_custom_text(root, scrollbar):
    text = Text(root)

    def proxy(*args):
        # Let the actual widget perform the requested action
        cmd = (text._orig,) + args
        result = text.tk.call(cmd)

        # Generate an event if something was added or deleted,
        # or the cursor position changed
        if (
            args[0] in ("insert", "replace", "delete")
            or args[0:3] == ("mark", "set", "insert")
            or args[0:2] == ("xview", "moveto")
            or args[0:2] == ("xview", "scroll")
            or args[0:2] == ("yview", "moveto")
            or args[0:2] == ("yview", "scroll")
        ):
            text.event_generate("<<Change>>", when="tail")

        # Return what the actual widget returned
        return result

    text._orig = text._w + "_orig"
    text.tk.call("rename", text._w, text._orig)
    text.tk.createcommand(text._w, proxy)
    text.configure(yscrollcommand=scrollbar.set)

    return text


def create_example(root):
    vsb = Scrollbar(root, orient="vertical")
    vsb.pack(side="right", fill="y")

    text = create_custom_text(root, vsb)
    text.pack(side="right", fill="both", expand=True)

    linenumbers_canvas = Canvas(root, width=30)
    linenumbers_canvas.pack(side="left", fill="y")

    redraw = create_text_line_numbers(linenumbers_canvas, text)

    text.bind("<<Change>>", lambda event: redraw())
    text.bind("<Configure>", lambda event: redraw())

    text.insert("end", "one\ntwo\nthree\n")
    text.insert("end", "four\n", ("bigfont",))
    text.insert("end", "five\n")

    return linenumbers_canvas

 
def toggle_linenumbers():
    """
    if linenumbers_button_var.get():
        linenumbers_canvas.pack(side="left", fill="y")
    else:
        linenumbers_canvas.pack_forget()
    """
    
    if linenumbers_button_var.get() == True:
        linenumbers_canvas.pack(side="left", fill="y")
    else:
        linenumbers_canvas.pack_forget()
















































# Hover effects for Toolbar Buttons, called in night_mode function
def hover(widget):
    widget.bind("<Enter>", func=lambda e: widget.config(bg="#202020", fg="white"))
    widget.bind("<Leave>", func=lambda e: widget.config(bg="#202020", fg="white"))

# Toggle Night Mode on and off
def night_mode():
    if night.get() == True:
        main_color = "#000000"
        second_color = "#373737"
        selection_highlight = "dark green"
        text_color = "green"

        # Hover effect colors
        def on_enter(e):
            e.widget['background'] = text_color
            e.widget['foreground'] = second_color         

        def on_exit(e):
            e.widget['background'] = second_color
            e.widget['foreground'] = text_color

        root.config(bg=main_color)
        status_bar.config(bg=main_color, fg=text_color)
        my_text.config(bg=second_color, insertbackground=text_color, selectforeground=selection_highlight)
        toolbar_frame.config(bg=main_color)
        
        # File Menu Colors
        file_menu.config(bg=main_color, fg=text_color)
        edit_menu.config(bg=main_color, fg=text_color)
        search_menu.config(bg=main_color, fg=text_color)
        format_menu.config(bg=main_color, fg=text_color)
        tools_menu.config(bg=main_color, fg=text_color)
        options_menu.config(bg=main_color, fg=text_color, selectcolor=text_color)

        # Toolbar Buttons
        bold_button.config(bg=second_color, fg=text_color)
        bold_button.bind("<Enter>", on_enter)
        bold_button.bind("<Leave>", on_exit)  

        italics_button.config(bg=second_color, fg=text_color)
        italics_button.bind("<Enter>", on_enter)
        italics_button.bind("<Leave>", on_exit)

        underline_button.config(bg=second_color, fg=text_color)
        underline_button.bind("<Enter>", on_enter)
        underline_button.bind("<Leave>", on_exit)

        strike_button.config(bg=second_color, fg=text_color)
        strike_button.bind("<Enter>", on_enter)
        strike_button.bind("<Leave>", on_exit)

        redo_button.config(bg=second_color, fg=text_color)
        redo_button.bind("<Enter>", on_enter)
        redo_button.bind("<Leave>", on_exit)

        undo_button.config(bg=second_color, fg=text_color)
        undo_button.bind("<Enter>", on_enter)
        undo_button.bind("<Leave>", on_exit)

        color_text_button.config(bg=second_color, fg=text_color)
        color_text_button.bind("<Enter>", on_enter)
        color_text_button.bind("<Leave>", on_exit)
        
        # Highlight Current Line      
        if highlighting.get() == True:
            my_text.tag_remove("current_line", 1.0, "end")
            highlight_current_line()
            my_text.tag_configure("current_line", background="#666666")
            my_text.tag_add("current_line", 1.0, "end")            
        else:
            my_text.tag_remove("current_line", 1.0, "end")
            my_text.tag_configure("current_line", background="#373737")
            my_text.tag_add("current_line", 1.0, "end")
        
    else:
        main_color = "SystemButtonFace"
        second_color = "SystemButtonFace"
        selection_highlight = "#999999"
        text_color = "black"

        # Hover effect colors
        def on_enter(e):
            e.widget['background'] = text_color
            e.widget['foreground'] = second_color         

        def on_exit(e):
            e.widget['background'] = second_color
            e.widget['foreground'] = text_color

        root.config(bg=main_color)
        status_bar.config(bg=main_color, fg=text_color)
        # Restore to widget background to basic white
        my_text.config(bg="white", insertbackground=text_color, selectforeground=selection_highlight)  
        toolbar_frame.config(bg=main_color)

        # File Menu Colors
        file_menu.config(bg=main_color, fg=text_color)
        edit_menu.config(bg=main_color, fg=text_color)
        search_menu.config(bg=main_color, fg=text_color)
        format_menu.config(bg=main_color, fg=text_color)
        tools_menu.config(bg=main_color, fg=text_color)
        options_menu.config(bg=main_color, fg=text_color, selectcolor=text_color)

        # Toolbar Buttons
        bold_button.config(bg=second_color, fg=text_color)
        bold_button.bind("<Enter>", on_enter)
        bold_button.bind("<Leave>", on_exit)  

        italics_button.config(bg=second_color, fg=text_color)
        italics_button.bind("<Enter>", on_enter)
        italics_button.bind("<Leave>", on_exit)

        underline_button.config(bg=second_color, fg=text_color)
        underline_button.bind("<Enter>", on_enter)
        underline_button.bind("<Leave>", on_exit)

        strike_button.config(bg=second_color, fg=text_color)
        strike_button.bind("<Enter>", on_enter)
        strike_button.bind("<Leave>", on_exit)

        redo_button.config(bg=second_color, fg=text_color)
        redo_button.bind("<Enter>", on_enter)
        redo_button.bind("<Leave>", on_exit)

        undo_button.config(bg=second_color, fg=text_color)
        undo_button.bind("<Enter>", on_enter)
        undo_button.bind("<Leave>", on_exit)

        color_text_button.config(bg=second_color, fg=text_color)
        color_text_button.bind("<Enter>", on_enter)
        color_text_button.bind("<Leave>", on_exit)

        # Highlight Current Line
        if highlighting.get() == True:
            my_text.tag_remove("current_line", 1.0, "end")
            my_text.tag_configure("current_line", background="#e9e9e9", selectbackground="#999999")
            my_text.tag_add("current_line", 1.0, "end")            
        else:
            my_text.tag_remove("current_line", 1.0, "end")
            my_text.tag_configure("current_line", background="white", selectbackground="yellow")
            my_text.tag_add("current_line", 1.0, "end")


# Toggle the visibility of the Status Bar on and off
# Credit goes to Stackoverflow users David and Roland Smith
# https://stackoverflow.com/questions/73516926/python-tkinter-status-bar-toolbar-toggle-on-off-example
def toggle_status_bar():
    pass
    """
    global status_bar
    if statusbar_is_on.get() == 1:
        # If the Status Bar is On, check if Night Mode is also On
        if night.get() == True:
            main_color = "#000000"
            second_color = "#373737"
            text_color = "green"
        
            status_bar = Label(root, text="Ready       ", anchor=E)
            status_bar.pack(fill=X, side=BOTTOM, ipady=15)
            status_bar.config(bg=main_color, fg=text_color)
        # If the Status Bar is On, but Night Mode is Off
        else: 
            main_color = "SystemButtonFace"
            second_color = "SystemButtonFace"
            text_color = "black"

            status_bar = Label(root, text="Ready       ", anchor=E)
            status_bar.pack(fill=X, side=BOTTOM, ipady=15)
            status_bar.config(bg=main_color, fg=text_color)
    else:
        # Off
        status_bar.destroy()
 
def status_bar():
    if status.get() == True:
        statusbar_is_on.set(1) 
    else:
        statusbar_is_on.set(0)

    toggle_status_bar()
"""

# Toggle Word Wrap on and off
def word_wrap():
    if wrap.get() == True:
        my_text.config(wrap="word")
        status_bar.config(text="Word Wrap On       ")
    else:
        my_text.config(wrap="none")


# ***************** Create the Drop Down Menus ***************** #

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
# file_menu.add_command(label="Exit", command=root.quit)
file_menu.add_command(label="Exit", command=exit_file)

# Add Edit Menu
edit_menu = Menu(my_menu, tearoff=False)
my_menu.add_cascade(label="Edit", menu=edit_menu)

edit_menu.add_command(label="Cut", command=lambda: cut_text(False), accelerator="(Ctrl+X)")
edit_menu.add_command(label="Copy", command=lambda: copy_text(False), accelerator="(Ctrl+C)")
edit_menu.add_command(label="Paste", command=lambda: paste_text(False), accelerator="(Ctrl+V)")
edit_menu.add_command(label="Delete", command=lambda: delete_text(False), accelerator="(Del)")
edit_menu.add_separator()
edit_menu.add_command(label="Select All", command=lambda: select_all(False), accelerator="(Ctrl+Shft+A)")
edit_menu.add_command(label="Clear All", command=lambda: clear_all(False))
edit_menu.add_separator()
edit_menu.add_command(label="Undo", command=my_text.edit_undo, accelerator="(Ctrl+Z)")
edit_menu.add_command(label="Redo", command=my_text.edit_redo, accelerator="(Ctrl+Y)")

# Add Search Menu
search_menu = Menu(my_menu, tearoff=False)
my_menu.add_cascade(label="Search", menu=search_menu)

search_menu.add_command(label="Find", command=lambda: find(False), accelerator="(Ctrl+F)")
search_menu.add_command(label="Fuzzy Find", command=fuzzy_find)
search_menu.add_command(label="Find Next", command=lambda: find_next(False), accelerator="(F3)")
search_menu.add_command(label="Replace", command=lambda: replace(False), accelerator="(Ctrl+H)")
search_menu.add_separator()
search_menu.add_command(label="Go To Line", command=go_to_line)

# Add Format Menu
format_menu = Menu(my_menu, tearoff=False)
my_menu.add_cascade(label="Format", menu=format_menu)

format_menu.add_command(label="Left Align", command=left_align)
format_menu.add_command(label="Right Align", command=right_align)
format_menu.add_command(label="Center Align", command=center_align)
format_menu.add_command(label="Justify Align", command=justify_align)
format_menu.add_separator()
format_menu.add_command(label="Selected Text", command=text_color)
format_menu.add_command(label="All Text", command=all_text_color)
format_menu.add_command(label="Background", command=bg_color)
format_menu.add_separator()
format_menu.add_command(label="Bold", command=bold_it)
format_menu.add_command(label="Italics", command=italics_it)
format_menu.add_command(label="Underline", command=underline_it)
format_menu.add_command(label="Strike", command=strike_it)

# Add Tools Menu
tools_menu = Menu(my_menu, tearoff=False)
my_menu.add_cascade(label="Tools", menu=tools_menu)

tools_menu.add_command(label="Change Case", command=case_tools)
tools_menu.add_command(label="Characters", command=character_tools)
tools_menu.add_command(label="Expressions", command=expression_tools)
tools_menu.add_command(label="Lines", command=line_tools)
tools_menu.add_command(label="Transform", command=transform_tools)
tools_menu.add_command(label="White Space", command=space_tools)
tools_menu.add_separator()
tools_menu.add_command(label="Statistical Analysis", command=statistic_tools)

# Add Options Menu
options_menu = Menu(my_menu, tearoff=False)
my_menu.add_cascade(label="Options", menu=options_menu)

# Toggle line highlighting on and off
highlighting = BooleanVar()
options_menu.add_checkbutton(label="Line Highlighting", onvalue=True, offvalue=False, variable=highlighting, command=toggle_line_highlighting)

# Toggle line numbering on and off
#numbering = BooleanVar()
#options_menu.add_checkbutton(label="Line Numbering", onvalue=True, offvalue=False, variable=numbering, command=line_numbering)

#linenumbers_button_var = BooleanVar(value=True)
#linenumbers_button = Checkbutton(root, text="Line Numbers", variable=linenumbers_button_var, command=toggle_linenumbers)
#linenumbers_button.pack(side="top", anchor="w")
#linenumbers_canvas = create_example(root)

linenumbers_button_var = BooleanVar()
options_menu.add_checkbutton(label="Line Numbering", onvalue=True, offvalue=False, variable=linenumbers_button_var, command=toggle_linenumbers)

# Toggle Night Mode on and off
night = BooleanVar()
options_menu.add_checkbutton(label="Night Mode", onvalue=True, offvalue=False, variable=night, command=night_mode)

# Toggle the visibility of the Status Bar on and off
status = BooleanVar()
options_menu.add_checkbutton(label="Status Bar", onvalue=True, offvalue=False, variable=status, command=status_bar)

# Toggle Word Wrap on and off
wrap = BooleanVar()
options_menu.add_checkbutton(label="Word Wrap", onvalue=True, offvalue=False, variable=wrap, command=word_wrap)


# ***************** Context Menus ***************** #

def my_popup(event):
    # Pass in coordinates of mouse
    context_menu.tk_popup(event.x_root, event.y_root)

# Create a Context Menu
context_menu = Menu(root, tearoff=False)
context_menu.add_command(label="Cut", command=lambda: cut_text(False))
context_menu.add_command(label="Copy", command=lambda: copy_text(False))
context_menu.add_command(label="Paste", command=lambda: paste_text(False))
context_menu.add_command(label="Delete", command=lambda: delete_text(False))

# Bind the mouse click to the menu function
root.bind("<Button-3>", my_popup)


# ***************** Bindings for Keyboard Shortcuts ***************** #

# File Menu Bindings
root.bind("<Control-Key-N>", new_file)
root.bind("<Control-Key-n>", new_file)
root.bind("<Control-Key-O>", open_file)
root.bind("<Control-Key-o>", open_file)
root.bind("<Control-Key-S>", save_file)
root.bind("<Control-Key-s>", save_file)
root.bind("<Control-Shift-S>", save_as_file)
root.bind("<Control-Shift-s>", save_as_file)
root.bind("<Control-Key-P>", print_file)
root.bind("<Control-Key-p>", print_file)
root.bind("<Control-Key-Q>", exit_file)
root.bind("<Control-Key-q>", exit_file)

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

# Search Bindings
root.bind('<Control-Key-F>', find)
root.bind('<Control-Key-f>', find) 
root.bind('<F3>', find_next)
root.bind('<Control-Key-H>', replace) 
root.bind('<Control-Key-h>', replace) 

# Font Bindings
root.bind("<Control-Key-B>", bold_it)
root.bind("<Control-Key-b>", bold_it)
root.bind("<Control-Key-I>", italics_it)
root.bind("<Control-Key-i>", italics_it)
root.bind("<Control-Key-U>", underline_it)
root.bind("<Control-Key-u>", underline_it)


# ***************** Toolbar Buttons ***************** #

main_color = "SystemButtonFace"
second_color = "SystemButtonFace"
text_color = "black"

# Hover effect colors
def on_enter(e):
    e.widget['background'] = text_color
    e.widget['foreground'] = second_color         

def on_exit(e):
    e.widget['background'] = second_color
    e.widget['foreground'] = text_color

# Bold Button
bold_button = Button(toolbar_frame, text="Bold", command=bold_it)
bold_button.grid(row=0, column=0, sticky=W, padx=5, pady=5)
bold_button.config(bg=second_color, fg=text_color)
bold_button.bind("<Enter>", on_enter)
bold_button.bind("<Leave>", on_exit)
# Italics Button
italics_button = Button(toolbar_frame, text="Italics", command=italics_it)
italics_button.grid(row=0, column=1, sticky=W, padx=5, pady=5)
italics_button.config(bg=second_color, fg=text_color)
italics_button.bind("<Enter>", on_enter)
italics_button.bind("<Leave>", on_exit)
# Underline Button
underline_button = Button(toolbar_frame, text="Underline", command=underline_it)
underline_button.grid(row=0, column=2, sticky=W, padx=5, pady=5)
underline_button.config(bg=second_color, fg=text_color)
underline_button.bind("<Enter>", on_enter)
underline_button.bind("<Leave>", on_exit)
# Strike Button
strike_button = Button(toolbar_frame, text="Strike", command=strike_it)
strike_button.grid(row=0, column=3, sticky=W, padx=5, pady=5)
strike_button.config(bg=second_color, fg=text_color)
strike_button.bind("<Enter>", on_enter)
strike_button.bind("<Leave>", on_exit)

# Undo Button
undo_button = Button(toolbar_frame, text="Undo", command=my_text.edit_undo)
undo_button.grid(row=0, column=4, sticky=W, padx=5, pady=5)
undo_button.config(bg=second_color, fg=text_color)
undo_button.bind("<Enter>", on_enter)
undo_button.bind("<Leave>", on_exit)
# Redo Button
redo_button = Button(toolbar_frame, text="Redo", command=my_text.edit_redo)
redo_button.grid(row=0, column=5, sticky=W, padx=5, pady=5)
redo_button.config(bg=second_color, fg=text_color)
redo_button.bind("<Enter>", on_enter)
redo_button.bind("<Leave>", on_exit)

# Text Color
color_text_button = Button(toolbar_frame, text="Text Color", command=text_color)
color_text_button.grid(row=0, column=6, sticky=W, padx=5, pady=5)
color_text_button.config(bg=second_color, fg=text_color)
color_text_button.bind("<Enter>", on_enter)
color_text_button.bind("<Leave>", on_exit)


# ********************************** #

linenumbers_button_var = BooleanVar(value=True)
linenumbers_button = Checkbutton(root, text="Line Numbers", variable=linenumbers_button_var, command=toggle_linenumbers)
linenumbers_button.pack(side="top", anchor="w")

linenumbers_canvas = create_example(root)
root.protocol("DELETE WINDOW", exit_file)
root.mainloop()

"""
Possible improvements:
    Change behavior of Bold function to highlight all text if Bold button
    is pushed a second time while highlight text partially tagged.
    
    Improve print function
    
    Change out the Clear All function for Delete
       
    Find a way to preserve formatting for text during saves
    
    Add Clear All Formatting function
    
    Organize code into Classes?
    
    Number the lines, then make the visibility of the lines optional
       
    Change Status bar to word count
    
    Use Status Bar visibility to include search
    
    Make color scheme customizable:
        main_color = "SystemButtonFace"
        second_color = "SystemButtonFace"
        text_color = "black"
"""
