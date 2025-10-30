# ops/edit/select_ops.py

from PyQt6.QtWidgets import QTextEdit

def select_all(main_window):
    """Select all text in the current editor."""
    editor = main_window.current_editor()
    if isinstance(editor, QTextEdit):
        editor.selectAll()
