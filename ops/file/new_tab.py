"""
Contains the callable function for creating a new tab.
"""
from PyQt6.QtWidgets import QTextEdit, QTabWidget
from typing import Callable

def create_new_tab(
    tab_widget: QTabWidget, 
    status_bar_update_callback: Callable, 
    title: str = "Untitled"
):
    """
    Creates a new tab with a QTextEdit widget and connects its signals.

    Args:
        tab_widget: The QTabWidget to add the new tab to.
        status_bar_update_callback: The function to call when the
                                     editor's state changes.
        title: The initial title for the new tab.
    """
    # Create the text editor widget
    editor = QTextEdit()
    
    # --- Signal Connections for Editor ---
    # When cursor moves, update status bar
    editor.cursorPositionChanged.connect(status_bar_update_callback)
    # When text changes, update status bar
    editor.textChanged.connect(status_bar_update_callback)
    
    # Add the editor as a new tab
    tab_index = tab_widget.addTab(editor, title)
    
    # Switch the view to the newly created tab
    tab_widget.setCurrentIndex(tab_index)
    
    # Give the editor focus so user can type immediately
    editor.setFocus()
