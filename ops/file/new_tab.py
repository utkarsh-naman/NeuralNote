# from PyQt6.QtWidgets import QTextEdit, QTabWidget
# from typing import Callable

# def create_new_tab(
#     tab_widget: QTabWidget, 
#     status_bar_update_callback: Callable, 
#     title: str = "Untitled"
# ):
#     editor = QTextEdit()
#     editor.cursorPositionChanged.connect(status_bar_update_callback)
#     editor.textChanged.connect(status_bar_update_callback)
#     tab_index = tab_widget.addTab(editor, title)
#     tab_widget.setCurrentIndex(tab_index)
#     editor.setFocus()


from PyQt6.QtWidgets import QTextEdit, QTabWidget
from typing import Callable

def create_new_tab(
    tab_widget: QTabWidget, 
    status_bar_update_callback: Callable, 
    title: str = "Untitled"
):
    editor = QTextEdit()

    # --- Connect text/cursor updates to status bar ---
    editor.cursorPositionChanged.connect(status_bar_update_callback)
    editor.textChanged.connect(status_bar_update_callback)

    # --- Add tab ---
    tab_index = tab_widget.addTab(editor, title)
    tab_widget.setCurrentIndex(tab_index)
    editor.setFocus()

    # --- Return editor so MainWindow can attach more signals (like dirty mark) ---
    return editor
