"""

Move the application preference concepts from:

toggle_status_bar
toggle_search_bar
toggle_line_highlighting
toggle_linenumbers
word_wrap
choose_custom_palette
checkbutton_selected
update_text_widget_color

"""


@dataclass
class EditorSettings:
    word_wrap: bool = True
    line_highlighting: bool = False
    show_status_bar: bool = True
    theme_name: str = "Default"






