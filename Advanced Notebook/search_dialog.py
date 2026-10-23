"""Find and replace dialog for the Qt word processor."""

from __future__ import annotations

import re

from PySide6.QtGui import QTextCursor, QTextDocument
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)


"""
Find next
Find previous
Replace
Replace all
Case sensitivity
Whole-word matching
Regular expressions
Search highlighting
Search result count
"""

"""
The old globals should disappear:

search_positions = []
current_result_index = -1
"""





class SearchDialog(QDialog):
    def __init__(self, editor: QTextEdit, parent=None):
        self.editor = editor
        self.search_positions = []
        self.current_result_index = -1








