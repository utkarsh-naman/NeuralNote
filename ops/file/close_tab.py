# from PyQt6.QtWidgets import QTabWidget

# def close_tab(tab_widget: QTabWidget, index: int):
#     """
#     Closes the tab at the given index.
#     (We'll add "do you want to save?" logic here later)
#     """
#     # Get the widget (QTextEdit) in the tab
#     widget = tab_widget.widget(index)
    
#     if widget:
#         # Remove the tab from the tab widget
#         tab_widget.removeTab(index)
#         widget.deleteLater()


from PyQt6.QtWidgets import QTabWidget, QMessageBox
from ops.file.save import save_file

def close_tab(self, tab_widget: QTabWidget, index: int):
    """
    Closes the tab at the given index.
    If the tab has unsaved changes (marked with '*'),
    ask the user whether to save before closing.
    """
    widget = tab_widget.widget(index)
    if not widget:
        return

    tab_title = tab_widget.tabText(index)
    is_dirty = tab_title.endswith("*")

    if is_dirty:
        reply = QMessageBox.question(
            self,
            "Unsaved Changes",
            f"Do you want to save changes to '{tab_title.strip('*')}'?",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save
        )

        if reply == QMessageBox.StandardButton.Save:
            tab_widget.setCurrentIndex(index)
            saved = save_file(self)  # ✅ check if save succeeded
            if not saved:
                return  # user canceled or save failed → keep tab open
        elif reply == QMessageBox.StandardButton.Cancel:
            return  # user canceled the dialog → keep tab open

    # --- Close tab safely ---
    tab_widget.removeTab(index)
    widget.deleteLater()

    if hasattr(self, "open_files") and widget in self.open_files:
        del self.open_files[widget]
