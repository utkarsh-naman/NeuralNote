from PyQt6.QtWidgets import QMessageBox, QFileDialog

from PyQt6.QtWidgets import QMessageBox, QFileDialog
from ops.file.recent import add_recent_file


def save_file(self):
    """Saves the current file. Opens 'Save As' if it's a new file."""
    editor = self.current_editor()
    if not editor:
        return False

    filepath = self.open_files.get(editor)
    if filepath:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(editor.toPlainText())

            clean_title = filepath.split('/')[-1]
            self.tab_widget.setTabText(self.tab_widget.currentIndex(), clean_title)

            add_recent_file(clean_title, filepath)
            return True  # ✅ success
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file: {e}")
            return False
    else:
        return save_file_as(self)  # ✅ propagate result


def save_file_as(self):
    """Saves the current file to a new location."""
    editor = self.current_editor()
    if not editor:
        return False

    filepath, _ = QFileDialog.getSaveFileName(
        self,
        "Save File As",
        "",
        "All Files (*);;Text Files (*.txt);;Python Files (*.py)"
    )

    if not filepath:
        return False  # ✅ user cancelled

    self.open_files[editor] = filepath
    return save_file(self)  # ✅ return True or False depending on success

    if success:
        add_recent_file(os.path.basename(filepath), filepath)

    return success


def save_all_files(self):
    """Saves all open files."""
    for i in range(self.tab_widget.count()):
        editor = self.tab_widget.widget(i)
        filepath = self.open_files.get(editor)
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(editor.toPlainText())
                
                clean_title = filepath.split('/')[-1]
                # self.tab_widget.setTabText(self.tab_widget.currentIndex(), clean_title)
                self.tab_widget.setTabText(i, clean_title)

                add_recent_file(clean_title, filepath)
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file {filepath}: {e}")
        # Note: This simple implementation doesn't prompt "Save As" for untitled files.
    QMessageBox.information(self, "Success", "All opened files have been saved.")
