# -*- coding: utf-8 -*-
"""
Simple Text Editor

Expanded version of the Codemy Tutorial:
https://www.youtube.com/watch?v=UlQRXJWUNBA 

Rebuilding Simple Text Editor from the skeleton of a working 
Line Numbering function to build the application to use the grid geometry manager
to create two columns: one for the line numbers and one for the text widget. 

Note:
You can't mix grid and pack on the same parent widget. You'll need to decide on
one and use it consistently for all child widgets.  To fix the error, you need
to choose to either use grid or pack for all the widgets inside the parent widget.

Changelog: Added menubar headers back in 
"""


# Import os and sys libraries to Open and Save files
import os, sys
# Import tkinter library
from tkinter import *
from tkinter import filedialog
from tkinter import font
from tkinter import messagebox
from tkinter import colorchooser
# Import TTK library to toggle Status Bar visibility
import tkinter.ttk as ttk   
import win32print
import win32api


# Tkinter adding line number to text widget
# Inspired by https://stackoverflow.com/questions/16369470/tkinter-adding-line-number-to-text-widget

# Function to redraw the line numbers on the canvas whenever the text in the text widget is changed
def create_text_line_numbers(canvas, text_widget):
    """
    # First, delete all existing text in the canvas
    # Next, find the starting index of the text widget, and iterate over all lines of text
    # For each line, calculate the vertical position and line number, and draw it on the canvas
    """
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


# Function to create the text widget 
def create_custom_text(root, scrollbar, linenumbers_canvas):
    """
    Creates the text widget, sets up a scrollbar, and binds the <<Change>> event
    to the create_text_line_numbers function.
    """
    text = Text(root)

    # Function to generate an event <<Change>> whenever something is added or deleted in the text widget 
    def proxy(*args):
        # Let the actual widget perform the requested action
        cmd = (text._orig,) + args
        result = text.tk.call(cmd)

        # Generate an event if something was added or deleted, or the cursor position changed
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

    # Rename the original method of the text widget and create a new one that will forward calls to it
    text._orig = text._w + "_orig"
    text.tk.call("rename", text._w, text._orig)
    text.tk.createcommand(text._w, proxy)
    text.configure(yscrollcommand=scrollbar.set)

    # Create two columns: one for the line numbers and one for the text widget
    # Line number canvas column (Left)
    linenumbers_canvas.grid(row=0, column=0, sticky="nsew")
    linenumbers_canvas.grid_propagate(False)
    linenumbers_canvas.configure(width=30)

    # Text widget column (Right)
    text.grid(row=0, column=1, sticky="nsew")

    root.grid_rowconfigure(0, weight=1, minsize=linenumbers_canvas.winfo_reqheight())
    # Configure the second column (Text) to stretch and shrink
    root.grid_columnconfigure(1, weight=1)

    """
    The linenumbers_canvas is now passed as an argument to create_custom_text,
    and is placed in the first column using grid. The second column is configured
    to stretch and shrink using columnconfigure.
    """

    # Bind the <<Change>> event to the create_text_line_numbers function to redraw the line numbers whenever the TEXT changes
    text.bind("<<Change>>", create_text_line_numbers(linenumbers_canvas, text))
    # Bind the <<Modified>> event to the create_text_line_numbers function to redraw the line numbers whenever the CONTENTS of the text widget are changed
    text.bind("<<Modified>>", create_text_line_numbers(linenumbers_canvas, text))
    # Bind the <Configure> event to the create_text_line_numbers function to redraw the line numbers whenever the SIZE of the text widget changes
    # Omit the following line and linenumbers_canvas won't add number until selected.
    text.bind("<Configure>", create_text_line_numbers(linenumbers_canvas, text))
    return text


# Shows or hides the line numbers canvas.  Called from Options menu
# Function modified to set the row and column for the canvas
def toggle_linenumbers():
    """
    In this modified function, the linenumbers_canvas is placed in row 0 and
    column 0 using the grid() method. The sticky parameter is set to "nsew" to make
    the canvas fill the entire cell.
    
    The root.grid_rowconfigure(0, minsize=linenumbers_canvas.winfo_reqheight()) call
    is used to make the row height equal to the canvas height, which ensures that
    the canvas and text widget have the same height.
    """
    if linenumbers_button_var.get():
        linenumbers_canvas.grid(row=0, column=0, sticky="nsew")
        root.grid_rowconfigure(0, minsize=linenumbers_canvas.winfo_reqheight())
    else:
        linenumbers_canvas.grid_forget()
        root.grid_rowconfigure(0, minsize=0)


# ***************** Create the Drop Down Menus ***************** #

# Create menu bar
def create_menu():
    # Create the menu bar
    menubar = Menu(root)
    root.config(menu=menubar)

    # Add File Menu heading to the menubar
    file_menu = Menu(menubar, tearoff=False)
    menubar.add_cascade(label="File", menu=file_menu)
    """
    file_menu.add_command(label="New", command=new_file)
    file_menu.add_command(label="Open", command=open_file)
    file_menu.add_command(label="Save", command=save_file)
    file_menu.add_command(label="Save As", command=save_as_file)
    file_menu.add_separator()
    file_menu.add_command(label="Print", command=print_file)
    file_menu.add_separator()
    # file_menu.add_command(label="Exit", command=root.quit)
    file_menu.add_command(label="Exit", command=exit_file)
    """
    # Add Edit Menu heading to the menubar
    edit_menu = Menu(menubar, tearoff=False)
    menubar.add_cascade(label="Edit", menu=edit_menu)
    """
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
    """
    # Add Search Menu heading to the menubar
    search_menu = Menu(menubar, tearoff=False)
    menubar.add_cascade(label="Search", menu=search_menu)
    """
    search_menu.add_command(label="Find", command=lambda: find(False), accelerator="(Ctrl+F)")
    search_menu.add_command(label="Fuzzy Find", command=fuzzy_find)
    search_menu.add_command(label="Find Next", command=lambda: find_next(False), accelerator="(F3)")
    search_menu.add_command(label="Replace", command=lambda: replace(False), accelerator="(Ctrl+H)")
    search_menu.add_separator()
    search_menu.add_command(label="Go To Line", command=go_to_line)
    """
    # Add Format Menu heading to the menubar
    format_menu = Menu(menubar, tearoff=False)
    menubar.add_cascade(label="Format", menu=format_menu)
    """
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
    """
    # Add Tools Menu heading to the menubar
    tools_menu = Menu(menubar, tearoff=False)
    menubar.add_cascade(label="Tools", menu=tools_menu)
    """
    tools_menu.add_command(label="Change Case", command=case_tools)
    tools_menu.add_command(label="Characters", command=character_tools)
    tools_menu.add_command(label="Expressions", command=expression_tools)
    tools_menu.add_command(label="Lines", command=line_tools)
    tools_menu.add_command(label="Transform", command=transform_tools)
    tools_menu.add_command(label="White Space", command=space_tools)
    tools_menu.add_separator()
    tools_menu.add_command(label="Statistical Analysis", command=statistic_tools)
    """
    # Add Options Menu heading to the menubar
    options_menu = Menu(menubar, tearoff=False)
    menubar.add_cascade(label="Options", menu=options_menu)
    """
    # Toggle line highlighting on and off
    highlighting = BooleanVar()
    options_menu.add_checkbutton(label="Line Highlighting", onvalue=True, offvalue=False, variable=highlighting, command=toggle_line_highlighting)
    """

    # Toggle line numbering on and off
    global linenumbers_button_var
    linenumbers_button_var = BooleanVar(value=True)  # Line numbering is on by default

    options_menu.add_checkbutton(
        label="Show Line Numbers",
        variable=linenumbers_button_var,
        onvalue=True,
        offvalue=False,
        command=toggle_linenumbers,)    

    """
    # Toggle line numbering on and off 
    show_line_numbers_var = BooleanVar()
    show_line_numbers_var.set(True)  # Line numbering is on by default
    options_menu.add_checkbutton(label="Line Numbers", variable=show_line_numbers_var, command=toggle_line_numbers)
    
    # Toggle Night Mode on and off
    night = BooleanVar()
    options_menu.add_checkbutton(label="Night Mode", onvalue=True, offvalue=False, variable=night, command=night_mode)
    
    # Toggle the visibility of the Status Bar on and off
    status = BooleanVar()
    options_menu.add_checkbutton(label="Status Bar", onvalue=True, offvalue=False, variable=status, command=status_bar)
    
    # Toggle Word Wrap on and off
    wrap = BooleanVar()
    options_menu.add_checkbutton(label="Word Wrap", onvalue=True, offvalue=False, variable=wrap, command=word_wrap)
    """







if __name__ == "__main__":
    # Create the main window
    root = Tk()

    # Create a vertical scrollbar for the linenumbers_canvas
    scrollbar = Scrollbar(root)
    scrollbar.grid(row=0, column=2, sticky="ns")

    # Create canvas to hold line numbers
    linenumbers_canvas = Canvas(root)
    linenumbers_canvas.grid(row=0, column=0, sticky="nsew")

    # Create text widget passing the root, scrollbar, and linenumbers_canvas as arguments.
    text = create_custom_text(root, scrollbar, linenumbers_canvas)   
    text.insert("end", "Type some text here...")

    text.insert("end", "one\ntwo\nthree\n")
    text.insert("end", "four\n", ("bigfont",))
    text.insert("end", "five\n")
    text.tag_configure("bigfont", font=("Helvetica", "24", "bold")) 

    # Create the menu bar    
    create_menu()

    # Starts the main event loop of the tkinter application
    root.mainloop()

