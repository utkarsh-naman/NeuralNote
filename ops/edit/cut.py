from PyQt6.QtWidgets import QTextEdit

def cut_text(main_window):
    editor = main_window.current_editor()
    if isinstance(editor, QTextEdit):
        editor.cut()
