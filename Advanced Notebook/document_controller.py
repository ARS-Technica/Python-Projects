"""
Simple Text Editor
Document Controller

Began as an expanded version of the Codemy Tutorial:
https://www.youtube.com/watch?v=UlQRXJWUNBA 

Document file operations for the Qt word processor.
Yes. The main issue is that text_editor 124.py currently combines at least eight responsibilities:

Application startup
Tkinter window construction
Document/file handling
Text editing
Formatting
Search
Themes/preferences
Regex-tool integration
To make it more Pythonic, separate those responsibilities into modules and replace global state with classes or injected dependencies.

Recommended project structure

For the Qt rewrite, the old Tkinter functions should be treated as a feature reference, not copied directly.

1. document_controller.py
This module should own document loading and saving.

Move the behavior from:

new_file
open_file
save_as_file
save_file


"""

'''
@dataclass
class DocumentState:
    path: Path | None = None
    modified: bool = False
    format: str = "html"
'''



# ***************** File Menu Functions

# Create New File Function
def new_file():
    # Delete previous text
    text.delete("1.0", END)
    window.title("New File")
    status_bar_label.config(text="New File       ")

    # Set variable for Open File name
    global open_status_name
    open_status_name = False

# Open File Function
def open_file():
    # Delete previous text
    text.delete("1.0", END)

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
    status_bar_label.config(text=f"{name}       ")
    name = name.replace(os.path.dirname(__file__), "")
    window.title(f"{name} - Text Editor")

    # Open the File
    text_file = open(text_file, 'r')
    stuff = text_file.read()
    # Add file to textbox
    text.insert(END, stuff)
    # Close the opened file
    text_file.close()

# Save As File Function
def save_as_file():
    # Use os.path.dirname(__file__) to find the current directory of the .py file
    text_file = filedialog.asksaveasfilename(defaultextension="*.*", initialdir=os.path.dirname(__file__), title="Save File", filetypes=[("Text Files", "*.txt"), ("Python Files", "*.py"), ("HTML Files", "*.html"), ("All Files", "*.*")])
    if text_file:
        # Update Status Bar
        name = text_file
        status_bar_label.config(text=f"{name}       ")
        name = name.replace(os.path.dirname(__file__), "")
        window.title(f"{name} - Text Editor")

        # Save the file
        text_file = open(text_file, "w")
        text_file.write(text.get(1.0, END))
        # Close the file
        text_file.close()

# Save File Function
def save_file():
    global open_status_name
    if open_status_name:
        # Save the file
        text_file = open(open_status_name, "w")
        text_file.write(text.get(1.0, END))
        # Close the file
        text_file.close()
        # Confirm that the file has been saved
        messagebox.showinfo("confirmation", "File Saved!")        
        status_bar_label.config(text=f"Saved: {open_status_name}       ")
    else:
        save_as_file()














'''
from __future__ import annotations
from pathlib import Path
from PySide6.QtWidgets import QTextEdit


RICH_TEXT_SUFFIXES = {".html", ".htm"}


class DocumentController:
    """
    Load and save a QTextEdit document without owning the main window.
    """

    def load(self, editor: QTextEdit, path: Path) -> None:
        content = path.read_text(encoding="utf-8")
        if path.suffix.lower() in RICH_TEXT_SUFFIXES:
            editor.setHtml(content)
        else:
            editor.setPlainText(content)
        editor.document().setModified(False)

    def save(self, editor: QTextEdit, path: Path) -> None:
        content = (
            editor.toHtml()
            if path.suffix.lower() in RICH_TEXT_SUFFIXES
            else editor.toPlainText()
        )
        path.write_text(content, encoding="utf-8")
        editor.document().setModified(False)

'''
