from PyQt6.QtWidgets import QTabWidget

def close_tab(tab_widget: QTabWidget, index: int):
    """
    Closes the tab at the given index.
    (We'll add "do you want to save?" logic here later)
    """
    # Get the widget (QTextEdit) in the tab
    widget = tab_widget.widget(index)
    
    if widget:
        # Remove the tab from the tab widget
        tab_widget.removeTab(index)
        # Delete the widget to free up memory
        widget.deleteLater()
