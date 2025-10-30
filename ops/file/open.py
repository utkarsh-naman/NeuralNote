# # from PyQt6.QtWidgets import (QFileDialog, QMessageBox)

# # def open_file(self):
# #         """Opens a file and displays its content in a new tab."""
# #         filepath, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Text Files (*.txt);;Python Files (*.py)")
# #         if filepath:
# #             try:
# #                 with open(filepath, 'r', encoding='utf-8') as f:
# #                     content = f.read()
                
# #                 # If the current tab is empty and unsaved, use it. Otherwise, create a new one.
# #                 editor = self.current_editor()
# #                 if editor and not self.open_files.get(editor) and not editor.toPlainText():
# #                     index = self.tabs.currentIndex()
# #                     self.tabs.setTabText(index, filepath.split('/')[-1])
# #                 else:
# #                     self.new_tab(filename=filepath.split('/')[-1])
# #                     editor = self.current_editor()

# #                 editor.setText(content)
# #                 self.open_files[editor] = filepath
# #             except Exception as e:
# #                 QMessageBox.critical(self, "Error", f"Could not open file: {e}")





import os
from PyQt6.QtWidgets import (QFileDialog, QMessageBox, QTextEdit)
from ops.file.recent import add_recent_file


# Import the new_tab function so we can create tabs
from ops.file.new_tab import create_new_tab

# def open_file(main_window, fullpath):
#     """
#     Opens a file dialog, reads a file, and displays its content in a tab.
    
#     :param main_window: The MainWindow instance.
#     """
    
#     # Use main_window as the parent for the dialog
#     filepath, _ = QFileDialog.getOpenFileName(
#         main_window, 
#         "Open File", 
#         "",  # Start directory
#         "All Files (*);;Text Files (*.txt);;Python Files (*.py)"
#     )
    
#     # If the user selected a file (didn't cancel)
#     if filepath:
#         try:
#             # Read the file content
#             with open(filepath, 'r', encoding='utf-8') as f:
#                 content = f.read()
            
#             # Get just the filename (e.g., "my_file.txt")
#             filename = os.path.basename(filepath)
            
#             # Get the current editor using the main window's helper
#             editor = main_window.current_editor() 
            
#             # Check if the current tab is new (unsaved) and empty
#             is_new_and_empty = (
#                 editor 
#                 and not main_window.open_files.get(editor)  # Not in our file map
#                 and not editor.toPlainText()               # Has no text
#             )

#             if is_new_and_empty:
#                 # Use the existing empty tab
#                 index = main_window.tab_widget.currentIndex()
#                 main_window.tab_widget.setTabText(index, filename)
#             else:
#                 # Create a new tab
#                 create_new_tab(
#                     main_window.tab_widget, 
#                     main_window._updateStatusBar, 
#                     filename
#                 )
#                 # Get the new editor we just created
#                 editor = main_window.current_editor() 

#             # Set the content and map this editor to its file path
#             editor.setText(content)
#             main_window.open_files[editor] = filepath

#             add_recent_file(filename, filepath)
            
#         except Exception as e:
#             QMessageBox.critical(main_window, "Error", f"Could not open file: {e}")
    
    

def open_file(main_window, path=None):
    """
    Opens a file either from a given path or via a dialog,
    then displays its content in a new/existing tab.
    """
    from ops.file.recent import add_recent_file  # keep inside to avoid circular imports

    if path:
        filepath = path
    else:
        filepath, _ = QFileDialog.getOpenFileName(
            main_window,
            "Open File",
            "",
            "All Files (*);;Text Files (*.txt);;Python Files (*.py)"
        )

    if not filepath:
        return  # user cancelled

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        filename = os.path.basename(filepath)
        editor = main_window.current_editor()

        is_new_and_empty = (
            editor
            and not main_window.open_files.get(editor)
            and not editor.toPlainText()
        )

        if is_new_and_empty:
            index = main_window.tab_widget.currentIndex()
            main_window.tab_widget.setTabText(index, filename)
        else:
            create_new_tab(main_window.tab_widget, main_window._updateStatusBar, filename)
            editor = main_window.current_editor()

        editor.setText(content)
        main_window.open_files[editor] = filepath

        # ✅ Add to recents
        add_recent_file(filename, filepath)

    except Exception as e:
        QMessageBox.critical(main_window, "Error", f"Could not open file: {e}")
