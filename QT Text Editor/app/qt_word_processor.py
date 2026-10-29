"""
Initial PySide6 word-processor foundation.

This is intentionally separate from the legacy Tkinter application while the
editor features are migrated incrementally.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QAction,
    QActionGroup,
    QFont,
    QIcon,
    QPainter,
    QPixmap,
    QTextCharFormat,
)

from PySide6.QtWidgets import (
    QApplication,
    QColorDialog,
    QFileDialog,
    QFontComboBox,
    QLabel,
    QMainWindow,
    QMessageBox,
    QInputDialog,
    QSpinBox,
    QStatusBar,
    QTextEdit,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

