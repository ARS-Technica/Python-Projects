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

from app.document_controller import DocumentController
from app.line_number_gutter import LineNumberTextEdit
from app.print_controller import PrintController
from app.search_bar import SearchBar
from app.search_dialog import SearchDialog
from app.settings import THEMES, EditorSettings

class WordProcessorWindow(QMainWindow):
    """
    Main window for the incremental Qt editor migration.
    """

    def _build_ui(self) -> None:
        self.setWindowTitle("Qt Word Processor")
        self.resize(1200, 750)
        central_widget = QWidget(self)
        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.addWidget(self.editor, 1)
        central_layout.addWidget(self.search_bar)
        self.setCentralWidget(central_widget)
        self.search_bar.hide()
        self.editor.setAcceptRichText(True)
        self.editor.setPlaceholderText("Start writing...")
        self.editor.setContextMenuPolicy(Qt.ContextMenuPolicy.DefaultContextMenu)

        file_menu = self.menuBar().addMenu("&File")
        self.file_menu = file_menu
        self.new_action = QAction("&New", self)
        self.open_action = QAction("&Open...", self)
        self.save_action = QAction("&Save", self)
        self.save_as_action = QAction("Save &As...", self)
        self.exit_action = QAction("E&xit", self)
        self.print_action = QAction("&Print...", self)
        self.export_pdf_action = QAction("Export &PDF...", self)
        self.new_action.setShortcut("Ctrl+N")
        self.open_action.setShortcut("Ctrl+O")
        self.save_action.setShortcut("Ctrl+S")
        file_menu.addActions(
            (
                self.new_action,
                self.open_action,
                self.save_action,
                self.save_as_action,
            )
        )
        file_menu.addSeparator()
        file_menu.addAction(self.print_action)
        file_menu.addAction(self.export_pdf_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)


        edit_menu = self.menuBar().addMenu("&Edit")
        self.edit_menu = edit_menu
        self.undo_action = QAction("&Undo", self)
        self.redo_action = QAction("&Redo", self)
        self.cut_action = QAction("Cu&t", self)
        self.copy_action = QAction("&Copy", self)
        self.paste_action = QAction("&Paste", self)
        self.delete_action = QAction("&Delete", self)
        self.select_all_action = QAction("Select &All", self)
        self.clear_all_action = QAction("Clear All", self)
        self.undo_action.setToolTip("Undo the last edit")
        self.redo_action.setToolTip("Redo the last undone edit")
        self.cut_action.setToolTip("Cut the selected text")
        self.copy_action.setToolTip("Copy the selected text")
        self.paste_action.setToolTip("Paste text from the clipboard")
        self.delete_action.setToolTip("Delete the selected text")
        self.select_all_action.setToolTip("Select the entire document")
        self.clear_all_action.setToolTip("Clear the entire document")
        self.undo_action.triggered.connect(self.editor.undo)
        self.redo_action.triggered.connect(self.editor.redo)
        self.cut_action.triggered.connect(self.editor.cut)
        self.copy_action.triggered.connect(self.editor.copy)
        self.paste_action.triggered.connect(self.editor.paste)
        self.delete_action.triggered.connect(self.delete_selected_text)
        self.select_all_action.triggered.connect(self.editor.selectAll)
        self.clear_all_action.triggered.connect(self.editor.clear)
        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.cut_action)
        edit_menu.addAction(self.copy_action)
        edit_menu.addAction(self.paste_action)
        edit_menu.addAction(self.delete_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.select_all_action)
        edit_menu.addAction(self.clear_all_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)
