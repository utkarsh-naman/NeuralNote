from __future__ import annotations
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, 
    QCheckBox, QVBoxLayout, QHBoxLayout
)
from PyQt6.QtGui import QTextDocument, QTextCursor
from PyQt6.QtCore import Qt

if TYPE_CHECKING:
    from main import MainWindow # To avoid circular import for type hinting

class FindReplaceWidget(QWidget):
    """
    A floating widget for Find & Replace functionality.
    It interacts with the currently active editor in the MainWindow.
    """
    def __init__(self, main_window: MainWindow):
        super().__init__(main_window)
        self.main_window = main_window
        self.init_ui()
        self.connect_signals()
        
        # Start hidden. The main window will show it.
        self.hide() 

    def init_ui(self):
        self.setWindowTitle("Find & Replace")
        # Set it as a "Tool" window so it floats above the main window
        self.setWindowFlags(Qt.WindowType.Tool)

        # --- Layouts ---
        main_layout = QVBoxLayout()
        find_layout = QHBoxLayout()
        replace_layout = QHBoxLayout()
        options_layout = QHBoxLayout()
        close_layout = QHBoxLayout()

        # --- Find Widgets ---
        find_label = QLabel("Find:")
        self.find_input = QLineEdit()
        self.find_next_btn = QPushButton("Find Next")
        self.find_prev_btn = QPushButton("Find Prev")

        find_layout.addWidget(find_label)
        find_layout.addWidget(self.find_input)
        find_layout.addWidget(self.find_next_btn)
        find_layout.addWidget(self.find_prev_btn)

        # --- Replace Widgets ---
        replace_label = QLabel("Replace:")
        self.replace_input = QLineEdit()
        self.replace_btn = QPushButton("Replace")
        self.replace_all_btn = QPushButton("Replace All")

        replace_layout.addWidget(replace_label)
        replace_layout.addWidget(self.replace_input)
        replace_layout.addWidget(self.replace_btn)
        replace_layout.addWidget(self.replace_all_btn)

        # --- Options Widgets ---
        self.case_sensitive_cb = QCheckBox("Case Sensitive")
        self.whole_word_cb = QCheckBox("Whole Word")
        options_layout.addWidget(self.case_sensitive_cb)
        options_layout.addWidget(self.whole_word_cb)
        options_layout.addStretch() # Push checkboxes to the left

        # --- Close Button ---
        self.close_btn = QPushButton("Close")
        close_layout.addStretch() # Push button to the right
        close_layout.addWidget(self.close_btn)

        # --- Assemble Layout ---
        main_layout.addLayout(find_layout)
        main_layout.addLayout(replace_layout)
        main_layout.addLayout(options_layout)
        main_layout.addLayout(close_layout)
        self.setLayout(main_layout)
        
        # --- Apply Dark Theme Styling ---
        self.setStyleSheet("""
            QWidget {
                background-color: #3c3c3c;
                color: #f0f0f0;
            }
            QPushButton {
                background-color: #555;
                border: 1px solid #666;
                padding: 4px 8px;
                min-width: 60px; /* Give buttons some space */
            }
            QPushButton:hover {
                background-color: #666;
            }
            QPushButton:pressed {
                background-color: #444;
            }
            QLineEdit {
                background-color: #2b2b2b;
                color: #f0f0f0;
                border: 1px solid #555;
                padding: 3px;
            }
            QCheckBox::indicator {
                width: 13px;
                height: 13px;
            }
            QCheckBox::indicator:unchecked {
                background-color: #2b2b2b;
                border: 1px solid #555;
            }
            QCheckBox::indicator:checked {
                background-color: #007acc; /* A highlight color */
                border: 1px solid #555;
            }
        """)

    def connect_signals(self):
        # Close button
        self.close_btn.clicked.connect(self.hide)

        # Find buttons
        self.find_next_btn.clicked.connect(self.find_next)
        self.find_prev_btn.clicked.connect(self.find_prev)
        # Allow pressing Enter in the find input to find next
        self.find_input.returnPressed.connect(self.find_next)

        # Replace buttons
        self.replace_btn.clicked.connect(self.replace_selection)
        self.replace_all_btn.clicked.connect(self.replace_all)

    def get_find_options(self) -> QTextDocument.FindFlag:
        """Helper to build the search flags from checkboxes."""
        options = QTextDocument.FindFlag(0)
        if self.case_sensitive_cb.isChecked():
            options |= QTextDocument.FindFlag.FindCaseSensitively
        if self.whole_word_cb.isChecked():
            options |= QTextDocument.FindFlag.FindWholeWords
        return options

    def find_next(self):
        editor = self.main_window.current_editor()
        if not editor: return
        
        find_text = self.find_input.text()
        if not find_text: return
        
        options = self.get_find_options()
        
        if not editor.find(find_text, options):
            # If not found, wrap to the top and search again
            cursor = editor.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            editor.setTextCursor(cursor)
            if not editor.find(find_text, options):
                self.main_window.statusBar().showMessage(f"'{find_text}' not found.", 2000)

    def find_prev(self):
        editor = self.main_window.current_editor()
        if not editor: return
        
        find_text = self.find_input.text()
        if not find_text: return
        
        # Add the FindBackward flag
        options = self.get_find_options() | QTextDocument.FindFlag.FindBackward
        
        if not editor.find(find_text, options):
            # If not found, wrap to the bottom and search again
            cursor = editor.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            editor.setTextCursor(cursor)
            if not editor.find(find_text, options):
                self.main_window.statusBar().showMessage(f"'{find_text}' not found.", 2000)

    def replace_selection(self):
        editor = self.main_window.current_editor()
        if not editor: return
        
        find_text = self.find_input.text()
        replace_text = self.replace_input.text()
        cursor = editor.textCursor()

        # Check if the current selection matches the find_text
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            
            # --- START FIX ---
            # We must use standard Python string comparison, not Qt methods
            
            is_case_sensitive = self.case_sensitive_cb.isChecked()
            
            match = False
            if is_case_sensitive:
                if selected_text == find_text:
                    match = True
            else:
                # Use .lower() for case-insensitive comparison
                if selected_text.lower() == find_text.lower():
                    match = True
            
            # If the selected text matches the find text (respecting case)...
            if match:
                cursor.insertText(replace_text)
            
            # --- END FIX ---
        
        # Automatically find the next occurrence
        self.find_next()

    def replace_all(self):
        editor = self.main_window.current_editor()
        if not editor: return
        
        find_text = self.find_input.text()
        replace_text = self.replace_input.text()
        
        if not find_text:
            return

        options = self.get_find_options()
        
        # Move cursor to the start to replace all
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        editor.setTextCursor(cursor)
        
        count = 0
        # Group all replacements into a single "Undo" action
        editor.textCursor().beginEditBlock()
        
        # Use document-based search for a reliable replace-all
        doc = editor.document()
        search_cursor = doc.find(find_text, editor.textCursor(), options)
        
        if search_cursor.isNull():
             self.main_window.statusBar().showMessage(f"'{find_text}' not found.", 2000)
             editor.textCursor().endEditBlock()
             return
        
        while not search_cursor.isNull():
            search_cursor.insertText(replace_text)
            count += 1
            # Find the next occurrence from the current position
            search_cursor = doc.find(find_text, search_cursor, options)
            
        editor.textCursor().endEditBlock()
        
        self.main_window.statusBar().showMessage(f"Replaced {count} occurrence(s).", 3000)

    def showEvent(self, event):
        """
        Called when the widget is shown.
        Pre-fills the find input with the editor's current selection.
        """
        super().showEvent(event)
        
        # Pre-fill find_input with current selection
        editor = self.main_window.current_editor()
        if editor:
            cursor = editor.textCursor()
            if cursor.hasSelection():
                self.find_input.setText(cursor.selectedText())
        
        self.find_input.setFocus()
        self.find_input.selectAll()