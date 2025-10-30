# ops/edit/delete_ops.py

from PyQt6.QtWidgets import QTextEdit

def delete_selected(main_window):
    """Delete the selected text in the current editor."""
    editor = main_window.current_editor()
    if isinstance(editor, QTextEdit):
        cursor = editor.textCursor()
        if cursor.hasSelection():
            cursor.removeSelectedText()
            editor.setTextCursor(cursor)


def delete_current_line(main_window):
    """Delete the line where the cursor currently is."""
    editor = main_window.current_editor()
    if isinstance(editor, QTextEdit):
        cursor = editor.textCursor()
        cursor.select(cursor.SelectionType.BlockUnderCursor)
        cursor.removeSelectedText()
        editor.setTextCursor(cursor)
