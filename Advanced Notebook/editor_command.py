"""
Move the editing behavior from:

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


"""
However, most basic edit operations do not need custom functions in Qt. QTextEdit already provides:
editor.cut()
editor.copy()
editor.paste()
editor.undo()
editor.redo()
editor.selectAll()
editor.clear()

"""



