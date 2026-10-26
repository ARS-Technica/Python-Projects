"""
Qt settings and theme support for the word processor.
"""

from __future__ import annotations
from dataclasses import dataclass
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QColorDialog, QMainWindow, QTextEdit


@dataclass(frozen=True)
class Theme:
    name: str
    window: str
    editor: str
    foreground: str
    selection: str


THEMES: dict[str, Theme] = {
    "Default": Theme("Default", "#f0f0f0", "#ffffff", "#000000", "#b8d7ff"),
    "Night Mode": Theme("Night Mode", "#000000", "#373737", "#008000", "#006400"),
    "Antique Ivory": Theme("Antique Ivory", "#faebd7", "#ffe4b5", "#333333", "#d2b48c"),
    "Arctic Breeze": Theme("Arctic Breeze", "#87ceeb", "#add8e6", "#333333", "#b0e0e6"),
    "Autumn Leaves": Theme("Autumn Leaves", "#683a03", "#b56700", "#fff3e1", "#ea5f00"),
    "Cherry Blossom": Theme("Cherry Blossom", "#ff85a2", "#ffc3a0", "#331f30", "#ff4d6d"),
    "Citrus Burst": Theme("Citrus Burst", "#ffd700", "#ff9900", "#333333", "#ffa500"),
    "Cool Mint": Theme("Cool Mint", "#4ae0c0", "#80ffe0", "#1e1e1e", "#2ee0c0"),
    "Crimson Velvet": Theme("Crimson Velvet", "#8b0000", "#b22222", "#f5f5f5", "#cd5c5c"),
    "Dark Violet": Theme("Dark Violet", "#1c0f1d", "#2f1f3b", "#ffffff", "#791e94"),
    "Deep Ocean": Theme("Deep Ocean", "#0e2846", "#124f7b", "#ffffff", "#00a8cc"),
    "Desert Mirage": Theme("Desert Mirage", "#c4975b", "#f1d1a5", "#3a1d0e", "#b57f4a"),
    "Dusty Rose": Theme("Dusty Rose", "#c08081", "#d6a9a8", "#333333", "#a97879"),
    "Electric Lime": Theme("Electric Lime", "#66ff00", "#a3ff00", "#000000", "#4dff00"),
    "Emerald Isle": Theme("Emerald Isle", "#008148", "#00a878", "#ffffff", "#005d3d"),
    "Forest Green": Theme("Forest Green", "#0c2619", "#115740", "#ffffff", "#00b347"),
    "Faded Denim": Theme("Faded Denim", "#98afc7", "#b0c4de", "#333333", "#7a8b8b"),
    "Gray Whisper": Theme("Gray Whisper", "#a9a9a9", "#c0c0c0", "#333333", "#d3d3d3"),
    "Golden Sand": Theme("Golden Sand", "#b48c30", "#ffc060", "#3c3636", "#e4a736"),
    "Lavender Dreams": Theme("Lavender Dreams", "#e6e6fa", "#d8bfd8", "#333333", "#9370db"),
    "Lemon Zest": Theme("Lemon Zest", "#fff44f", "#fff68f", "#333333", "#ffec40"),
    "Midnight Blue": Theme("Midnight Blue", "#03031b", "#14146b", "#ffffff", "#3b3bcf"),
    "Monokai": Theme("Monokai", "#272822", "#3e3d32", "#f8f8f2", "#f92672"),
    "Mystic Forest": Theme("Mystic Forest", "#1a3a2a", "#325d4a", "#f0f0f0", "#78afa1"),
    "Ocean": Theme("Ocean", "#007bff", "#80c2ff", "#ffffff", "#003eff"),
    "Pastel": Theme("Pastel", "#f9e0e3", "#e5eaf1", "#3d3e43", "#fd9860"),
    "Royal Blue": Theme("Royal Blue", "#0a1172", "#1839a9", "#ffffff", "#6f6ec4"),
    "Quiet Mist": Theme("Quiet Mist", "#d3dde7", "#e3eaf1", "#333333", "#c2d7e1"),
    "Rose Gold": Theme("Rose Gold", "#cc7b63", "#e8ad99", "#230c0f", "#b66d4c"),
    "Royal Purple": Theme("Royal Purple", "#2c0f4c", "#5d2b78", "#ffffff", "#a756b8"),
    "Solarized Light": Theme("Solarized Light", "#fdf6e3", "#eee8d5", "#657b83", "#93a1a1"),
    "Rustic Charm": Theme("Rustic Charm", "#8b4513", "#cd853f", "#f5f5f5", "#a0522d"),
    "Slate Gray": Theme("Slate Gray", "#708090", "#778899", "#ffffff", "#a9a9a9"),
    "Soft Coral": Theme("Soft Coral", "#ff6f61", "#ffb6b0", "#3c3636", "#ff8b80"),
    "Soft Lavender": Theme("Soft Lavender", "#c9a0dc", "#e6e6fa", "#333333", "#b894c6"),
    "Sunny Day": Theme("Sunny Day", "#facb15", "#fff5a7", "#333333", "#ff8200"),
    "Sunset": Theme("Sunset", "#ff6b35", "#ffabab", "#ffffff", "#ff4d00"),
    "Taupe Elegance": Theme("Taupe Elegance", "#483c32", "#635b53", "#f5f5f5", "#7c746c"),
    "Teal Twist": Theme("Teal Twist", "#008080", "#20b2aa", "#ffffff", "#00ced1"),
    "Vintage Rose": Theme("Vintage Rose", "#8b475d", "#c77b95", "#f1f0eb", "#d25f80"),
}


class EditorSettings:
    """
    Apply editor-view options and themes.
    """

    def __init__(self, window: QMainWindow, editor: QTextEdit) -> None:
        self.window = window
        self.editor = editor
        self.current_theme = "Default"
        self._line_highlighting_enabled = False

    def apply_theme(self, name: str) -> None:
        theme = THEMES[name]
        self.current_theme = name
        palette = self.window.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(theme.window))
        palette.setColor(QPalette.ColorRole.Base, QColor(theme.editor))
        palette.setColor(QPalette.ColorRole.Text, QColor(theme.foreground))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(theme.selection))
        self.window.setPalette(palette)
        self.editor.setStyleSheet(
            "QTextEdit {"
            f" background-color: {theme.editor};"
            f" color: {theme.foreground};"
            f" selection-background-color: {theme.selection};"
            "}"
        )

    def choose_custom_palette(self) -> None:
        color = QColorDialog.getColor(
            self.editor.palette().color(QPalette.ColorRole.Base),
            self.window,
            "Choose editor palette",
        )
        if color.isValid():
            self.editor.setStyleSheet(
                "QTextEdit {"
                f" background-color: {color.name()};"
                "}"
            )

    def set_word_wrap(self, enabled: bool) -> None:
        mode = (
            QTextEdit.LineWrapMode.WidgetWidth
            if enabled
            else QTextEdit.LineWrapMode.NoWrap
        )
        self.editor.setLineWrapMode(mode)

    def set_status_bar_visible(self, visible: bool) -> None:
        self.window.statusBar().setVisible(visible)

    def set_line_numbers_visible(self, visible: bool) -> None:
        area = getattr(self.editor, "line_number_area", None)
        if area is None:
            return

        area.setVisible(visible)
        self.editor.setViewportMargins(
            self.editor.line_number_width() if visible else 0,
            0,
            0,
            0,
        )
        area.update()

    def set_line_highlighting_enabled(self, enabled: bool) -> None:
        self._line_highlighting_enabled = enabled
        self.update_current_line()

    def update_current_line(self) -> None:
        selections: list[QTextEdit.ExtraSelection] = []

        if self._line_highlighting_enabled:
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(QColor("#e9e9e9"))
            selection.cursor = self.editor.textCursor()
            selection.cursor.clearSelection()
            selections.append(selection)

        self.editor.setExtraSelections(selections)

