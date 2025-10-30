from PyQt6.QtWidgets import QInputDialog, QTextEdit

def goto_line(main_window):
    editor = main_window.current_editor()
    if not isinstance(editor, QTextEdit):
        return

    max_lines = editor.document().blockCount()
    line, ok = QInputDialog.getInt(main_window, "Go to Line", f"Enter line number (1–{max_lines}):", 1, 1, max_lines)

    if ok:
        cursor = editor.textCursor()
        cursor.movePosition(cursor.MoveOperation.Start)
        cursor.movePosition(cursor.MoveOperation.Down, cursor.MoveMode.MoveAnchor, line - 1)
        editor.setTextCursor(cursor)
