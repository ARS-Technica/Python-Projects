"""
Initial PySide6 word-processor foundation.

This is intentionally separate from the legacy Tkinter application while the
editor features are migrated incrementally.
"""

from __future__ import annotations

from pathlib import Path
from PySide6.QtGui import QTextDocument
from PySide6.QtPrintSupport import QPrintDialog, QPrinter
from PySide6.QtWidgets import QFileDialog, QMainWindow, QTextEdit


class PrintController:
  """
  Provide print and PDF export operations.
  """

  pass

