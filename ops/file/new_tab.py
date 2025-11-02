from PyQt6.QtWidgets import QTextEdit, QTabWidget
from typing import Callable, Type # 🌟 ADDED 'Type' here

def create_new_tab(
    tab_widget: QTabWidget, 
    status_bar_update_callback: Callable, 
    title: str = "Untitled", # 🌟 COMMA ADDED HERE
    editor_class: Type[QTextEdit] = QTextEdit, 
    main_window=None
):
    """
    Creates a new tab with an editor and connects status bar signals.
    
    This function has been updated to accept a custom editor class (like GrammarTextEdit) 
    and a reference to the main window for custom functionality (like NLP).
    """
    
    # 🌟 Instantiate the custom editor class instead of hardcoding QTextEdit
    if main_window:
        editor = editor_class(main_window=main_window)
    else:
        # Fallback for standard QTextEdit or if main_window is not strictly needed
        editor = editor_class() 

    # --- Connect text/cursor updates to status bar ---
    editor.cursorPositionChanged.connect(status_bar_update_callback)
    editor.textChanged.connect(status_bar_update_callback)

    # --- Add tab ---
    tab_index = tab_widget.addTab(editor, title)
    tab_widget.setCurrentIndex(tab_index)
    editor.setFocus()

    # --- Return editor so MainWindow can attach more signals (like dirty mark) ---
    return editor