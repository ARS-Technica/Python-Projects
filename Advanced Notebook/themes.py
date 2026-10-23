"""
color_schemes
main_color
second_color
selection_highlight
text_color
line_highlight
Theme conversion/application functions


"""

@dataclass(frozen=True)
class Theme:
    name: str
    window_background: str
    editor_background: str
    editor_foreground: str
    selection_background: str
    selection_foreground: str

