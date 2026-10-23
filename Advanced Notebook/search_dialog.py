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
find_all
find_next
find_previous
next_result
clear_find_results
paste_clipboard_to_search
replace

"""
