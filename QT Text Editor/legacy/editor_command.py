

"""
cut_text
copy_text
paste_text
delete_text
copy_all
select_all
clear_all
go_to_line_number
go_to_line
go_to_next_line
go_to_previous_line


"""

# ***************** Edit Menu Functions

# Cut Text
def cut_text(event):
    # "Event" because the function is listening for the key binding.
    global selected
    # Check if keyboad shortcut was used
    if event:
        # If Cut is being invoked by keyboard, grab what's on the clipboard
        selected = window.clipboard_get()
    else:
        """
        Using Try/Except here rather than if/else avoids the following error,
        which results from attempting to use Cut without first selecting text.

        return self.tk.call(('selection', 'get') + self._options(kw))
        _tkinter.TclError: PRIMARY selection doesn't exist or form "STRING" not defined
        """
        # if text.selection_get():
        try:
            # Grab selected text from text box
            selected = text.selection_get()
            # Delete selected text from text box
            text.delete("sel.first", "sel.last")
            # Clear the Clipboard, then append text
            window.clipboard_clear()
            window.clipboard_append(selected)
        except:
            # Alert user that no text has been selected
            status_bar.bell() # Windows bell sound
            status_bar_label.config(text="No text has been selected       ")
            # messagebox.showinfo("alert", "No text has been selected")        
            # status_bar_label.config(text="Ready       ")

# Copy Text
def copy_text(event):
    global selected
    # Check if keyboad shortcut was used
    if event:
        # If Copy is being invoked by keyboard, grab what's on the clipboard
        selected = window.clipboard_get()
    else:
        """
        Using Try/Except here rather than if/else avoids the following error,
        which results from attempting to use Copy without first selecting text.

        return self.tk.call(('selection', 'get') + self._options(kw))
        _tkinter.TclError: PRIMARY selection doesn't exist or form "STRING" not defined
        """
        # if text.selection_get():
        try:
            # Grab selected text from text box
            selected = text.selection_get()
            # Clear the Clipboard, then append text
            window.clipboard_clear()
            window.clipboard_append(selected)
        except:
            # Alert user that no text has been selected
            status_bar.bell() # Windows bell sound
            status_bar_label.config(text="No text has been selected       ")
            # messagebox.showinfo("alert", "No text has been selected")        
            # status_bar_label.config(text="Ready       ")        

# Paste Text
def paste_text(event):
    global selected 
    # Check if keyboad shortcut was used
    if event:
        # If Paste is being invoked by keyboard, grab what's on the clipboard
        selected = window.clipboard_get()
    else:
        if selected:
            position = text.index(INSERT)
            text.insert(position, selected)

# Delete Selected Text
def delete_text(event):
    # Check if any text is selected, otherwise app throws an error
    if text.tag_ranges("sel"):
        # Delete selected text
        text.delete("sel.first", "sel.last")
    else:
        # Alert user that no text has been selected
        status_bar.bell() # Windows bell sound
        status_bar_label.config(text="No text has been selected       ")
        # messagebox.showinfo("alert", "No text has been selected")        
        # status_bar_label.config(text="Ready       ")             

# Copy All Text
def copy_all(event):
    pass

# Select All Text
def select_all(event):
    # Add sel tag to select all text
    text.tag_add('sel', '1.0', 'end')

# Clear All Text
def clear_all(event):
    text.delete(1.0, END)
    # Delete function doesn't require quotation marks




# ***************** Go To Line Functions

# Store the previously highlighted line number
previous_highlighted_line = None

def go_to_line_number():   
    # Ask the user for a line number to highlight
    line_number = simpledialog.askinteger("Line Number", "Enter the line number:")
    return line_number

def go_to_line(text_widget, line_number):
    # total_lines = int(text_widget.index('end-1c').split('.')[0])
    # if 1 <= line_number <= total_lines:
    # Checks if line_number is None and doesn't perform the comparison if user cancels the input dialog
    # Otherwise, pressng cancel results in error: "TypeError: '<=' not supported between instances of 'int' and 'NoneType'"
       
    # Ensure the line number is within a valid range
    if line_number is not None and 1 <= line_number <= int(text_widget.index('end-1c').split('.')[0]):
        # Clear previous highlighting
        clear_highlighting(text_widget)
        # Scroll to the line (line_number - 1)
        text_widget.see(f"{line_number}.0")
        # Highlight the line (line_number - 1)
        start_index = f"{line_number}.0"
        end_index = f"{line_number + 1}.0"
        text_widget.tag_add("highlight", start_index, end_index)
        text_widget.tag_configure("highlight", background=line_highlight)  # You can customize the highlight color
        # Update the previously highlighted line
        global previous_highlighted_line
        previous_highlighted_line = line_number

def go_to_line(text_widget, line_number):
    # total_lines = int(text_widget.index('end-1c').split('.')[0])
    # if 1 <= line_number <= total_lines:
    # Checks if line_number is None and doesn't perform the comparison if user cancels the input dialog
    # Otherwise, pressng cancel results in error: "TypeError: '<=' not supported between instances of 'int' and 'NoneType'"
       
    # Ensure the line number is within a valid range
    if line_number is not None and 1 <= line_number <= int(text_widget.index('end-1c').split('.')[0]):
        # Clear previous highlighting
        clear_highlighting(text_widget)
        # Scroll to the line (line_number - 1)
        text_widget.see(f"{line_number}.0")
        # Highlight the line (line_number - 1)
        start_index = f"{line_number}.0"
        end_index = f"{line_number + 1}.0"
        text_widget.tag_add("highlight", start_index, end_index)
        text_widget.tag_configure("highlight", background=line_highlight)  # You can customize the highlight color
        # Update the previously highlighted line
        global previous_highlighted_line
        previous_highlighted_line = line_number
        
        # Move the cursor to the beginning (.0) of line_number
        text_widget.mark_set("insert", f"{line_number}.0")
        
        # Ensure the cursor is visible
        text_widget.see("insert")
        
        # Set the focus in the textbox
        text_widget.focus_set() 

"""
def go_to_next_line(text_widget):
    if previous_highlighted_line is None:
        # If there's no previous highlight, start from the first line
        go_to_line(text_widget, 1)
    else:
        # Get the current line number
        current_line = int(previous_highlighted_line)
        # Calculate the next line number
        next_line = current_line + 1
        if next_line > int(text_widget.index('end-1c').split('.')[0]):
            # Wrap around to the first line if at the end
            next_line = 1
        # Scroll and highlight the next line
        go_to_line(text_widget, next_line)
"""

def go_to_previous_line(text_widget):
    if previous_highlighted_line is None:
        # If there's no previous highlight, start from the first line
        go_to_line(text_widget, 1)
    else:
        # Get the current line number
        current_line = int(previous_highlighted_line)
        # Calculate the previous line number
        previous_line = current_line - 1
        if previous_line < 1:
            # Wrap around to the last line if at the beginning
            previous_line = int(text_widget.index('end-1c').split('.')[0])
        # Scroll and highlight the previous line
        go_to_line(text_widget, previous_line)
