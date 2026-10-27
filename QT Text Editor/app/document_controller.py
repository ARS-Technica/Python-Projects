"""
Document loading and saving for the Qt word processor.
"""

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

