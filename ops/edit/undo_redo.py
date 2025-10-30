# ops/edit/undo_redo.py

from PyQt6.QtWidgets import QTextEdit

def undo_action(main_window):
    """Perform undo on the current text editor."""
    editor = main_window.current_editor()
    if isinstance(editor, QTextEdit):
        editor.undo()


def redo_action(main_window):
    """Perform redo on the current text editor."""
    editor = main_window.current_editor()
    if isinstance(editor, QTextEdit):
        editor.redo()
