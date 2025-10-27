from PyQt6.QtWidgets import QMessageBox
from ops.file.save import save_file

def close_window(self):
    """
    Closes the current window safely.
    Prompts to save unsaved (dirty) tabs before exit.
    """
    if not hasattr(self, "tab_widget"):
        self.close()
        return

    unsaved_tabs = []
    dirty_indices = []

    # --- Find unsaved (dirty) tabs ---
    for i in range(self.tab_widget.count()):
        title = self.tab_widget.tabText(i)
        if title.endswith("*"):
            unsaved_tabs.append(title.strip("*"))
            dirty_indices.append(i)

    # --- If unsaved tabs exist, prompt user ---
    if unsaved_tabs:
        reply = QMessageBox.question(
            self,
            "Unsaved Changes",
            f"The following files have unsaved changes:\n\n"
            + "\n".join(f"• {name}" for name in unsaved_tabs)
            + "\n\nDo you want to save them before closing this window?",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save
        )

        if reply == QMessageBox.StandardButton.Save:
            for i in dirty_indices:
                self.tab_widget.setCurrentIndex(i)
                saved = save_file(self)
                if not saved:
                    return  # Cancelled during Save As → abort close
        elif reply == QMessageBox.StandardButton.Cancel:
            return  # Abort close

    # ✅ Now actually close the window
    self.close()
