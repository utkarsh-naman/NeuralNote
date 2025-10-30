import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QStatusBar, QLabel, QTabWidget, QWidget
)
from PyQt6.QtGui import QFont, QIcon, QAction, QKeySequence
from PyQt6.QtCore import Qt

# --- File operations ---
from ops.file.new_tab import create_new_tab
from ops.file.new_window import create_new_window
from ops.file.exit import exit_app
from ops.file.open import open_file
from ops.file.save import save_file, save_file_as, save_all_files
from ops.file.close_tab import close_tab

# --- Edit operations ---
from ops.edit.undo_redo import undo_action, redo_action
from ops.edit.delete_ops import delete_selected, delete_current_line
from ops.edit.select_ops import select_all

# --- UI ---
from ui.custom_tab_bar import CustomTabBar


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("NeuralNote")
        self.resize(1000, 700)
        self.open_files = {}  # Track open file paths

        # --- Dark Theme Styles ---
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #f0f0f0;
            }
            QMenuBar {
                background-color: #3c3c3c;
                color: #f0f0f0;
            }
            QMenuBar::item:selected {
                background-color: #555;
            }
            QMenu {
                background-color: #3c3c3c;
                color: #f0f0f0;
            }
            QMenu::item:selected {
                background-color: #555;
            }
            QStatusBar {
                background-color: #3c3c3c;
                color: #f0f0f0;
            }
            QTextEdit {
                background-color: #2b2b2b;
                color: #f0f0f0;
                border: none;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11pt;
            }
        """)

        self._createMenuBar()
        self._createStatusBar()
        self._createTabs()
        self._updateStatusBar()

    # -------------------------------
    # Tab and Editor Handling
    # -------------------------------
    def _mark_dirty(self, editor):
        index = self.tab_widget.indexOf(editor)
        if index == -1:
            return

        title = self.tab_widget.tabText(index)
        if not title.endswith("*"):
            self.tab_widget.setTabText(index, title + "*")

    def _createTabs(self):
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)

        custom_bar = CustomTabBar()
        self.tab_widget.setTabBar(custom_bar)
        custom_bar.tabCloseRequested.connect(lambda i: close_tab(self, self.tab_widget, i))
        self.tab_widget.tabCloseRequested.connect(lambda i: close_tab(self, self.tab_widget, i))
        self.tab_widget.currentChanged.connect(custom_bar.updateAllTabIcons)
        self.tab_widget.currentChanged.connect(self._updateStatusBar)

        editor = create_new_tab(self.tab_widget, self._updateStatusBar, "Untitled")
        editor.textChanged.connect(lambda e=editor: self._mark_dirty(e))
        self.setCentralWidget(self.tab_widget)

    def current_editor(self) -> QTextEdit | None:
        widget = self.tab_widget.currentWidget()
        if isinstance(widget, QTextEdit):
            return widget
        return None

    # -------------------------------
    # Menu Bar
    # -------------------------------
    def _createMenuBar(self):
        menu_bar = self.menuBar()

        # ---------- FILE MENU ----------
        file_menu = menu_bar.addMenu("&File")

        new_tab_action = QAction("&New Tab", self)
        new_tab_action.setShortcuts([QKeySequence.StandardKey.New, QKeySequence("Ctrl+T")])
        new_tab_action.triggered.connect(self.on_new_tab_action)
        file_menu.addAction(new_tab_action)

        new_window_action = QAction("New &Window", self)
        new_window_action.setShortcut(QKeySequence("Ctrl+Shift+N"))
        new_window_action.triggered.connect(self.on_new_window_action)
        file_menu.addAction(new_window_action)

        open_action = QAction("Open", self)
        open_action.setShortcut(QKeySequence("Ctrl+O"))
        open_action.triggered.connect(self.on_open_file_action)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        save_action.triggered.connect(lambda: save_file(self))
        file_menu.addAction(save_action)

        save_as_action = QAction("Save As...", self)
        save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_as_action.triggered.connect(lambda: save_file_as(self))
        file_menu.addAction(save_as_action)

        save_all_action = QAction("Save All", self)
        save_all_action.triggered.connect(lambda: save_all_files(self))
        file_menu.addAction(save_all_action)

        file_menu.addSeparator()

        close_tab_action = QAction("Close Tab", self)
        close_tab_action.setShortcut(QKeySequence("Ctrl+W"))
        close_tab_action.triggered.connect(lambda: close_tab(self, self.tab_widget, self.tab_widget.currentIndex()))
        file_menu.addAction(close_tab_action)

        close_window_action = QAction("Close Window", self)
        close_window_action.setShortcut(QKeySequence("Ctrl+Shift+W"))
        close_window_action.triggered.connect(self.close)
        file_menu.addAction(close_window_action)

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(exit_app)
        file_menu.addAction(exit_action)

        # ---------- EDIT MENU ----------
        edit_menu = menu_bar.addMenu("&Edit")

        # Undo / Redo
        undo_act = QAction("Undo", self)
        undo_act.setShortcut(QKeySequence.StandardKey.Undo)
        undo_act.triggered.connect(lambda: undo_action(self))
        edit_menu.addAction(undo_act)

        redo_act = QAction("Redo", self)
        redo_act.setShortcut(QKeySequence.StandardKey.Redo)
        redo_act.triggered.connect(lambda: redo_action(self))
        edit_menu.addAction(redo_act)

        edit_menu.addSeparator()

        # Delete
        delete_sel_act = QAction("Delete Selection", self)
        delete_sel_act.setShortcut(QKeySequence("Del"))
        delete_sel_act.triggered.connect(lambda: delete_selected(self))
        edit_menu.addAction(delete_sel_act)

        delete_line_act = QAction("Delete Current Line", self)
        delete_line_act.setShortcut(QKeySequence("Ctrl+Shift+D"))
        delete_line_act.triggered.connect(lambda: delete_current_line(self))
        edit_menu.addAction(delete_line_act)

        edit_menu.addSeparator()

        # Select All
        select_all_act = QAction("Select All", self)
        select_all_act.setShortcut(QKeySequence.StandardKey.SelectAll)
        select_all_act.triggered.connect(lambda: select_all(self))
        edit_menu.addAction(select_all_act)

    # -------------------------------
    # File Menu Actions
    # -------------------------------
    def on_new_tab_action(self):
        editor = create_new_tab(self.tab_widget, self._updateStatusBar, "Untitled")
        editor.textChanged.connect(lambda e=editor: self._mark_dirty(e))

    def on_new_window_action(self):
        create_new_window(MainWindow)

    def on_open_file_action(self):
        open_file(self)
        editor = self.current_editor()
        if editor:
            editor.textChanged.connect(lambda e=editor: self._mark_dirty(e))

    # -------------------------------
    # Status Bar
    # -------------------------------
    def _createStatusBar(self):
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)

        self.cursor_pos_label = QLabel("Ln 1, Col 1")
        self.char_count_label = QLabel("0 characters")
        self.zoom_label = QLabel("100%")
        self.line_ending_label = QLabel("Windows (CRLF)")
        self.encoding_label = QLabel("UTF-8")

        status_bar.addPermanentWidget(self.cursor_pos_label)
        status_bar.addPermanentWidget(self.char_count_label)
        status_bar.addPermanentWidget(self.zoom_label)
        status_bar.addPermanentWidget(self.line_ending_label)
        status_bar.addPermanentWidget(self.encoding_label)

    def _updateStatusBar(self):
        current_editor = self.tab_widget.currentWidget()
        if isinstance(current_editor, QTextEdit):
            cursor = current_editor.textCursor()
            line = cursor.blockNumber() + 1
            col = cursor.columnNumber() + 1
            self.cursor_pos_label.setText(f"Ln {line}, Col {col}")
            char_count = len(current_editor.toPlainText())
            self.char_count_label.setText(f"{char_count} characters")
        else:
            self.cursor_pos_label.setText("Ln 1, Col 1")
            self.char_count_label.setText("0 characters")

    # -------------------------------
    # Window Close Event
    # -------------------------------
    def closeEvent(self, event):
        """Prompt to save unsaved tabs before closing."""
        from PyQt6.QtWidgets import QMessageBox

        unsaved_tabs = []
        for i in range(self.tab_widget.count()):
            title = self.tab_widget.tabText(i)
            if title.endswith("*"):
                unsaved_tabs.append(i)

        if not unsaved_tabs:
            event.accept()
            return

        msg = QMessageBox(self)
        msg.setWindowTitle("Unsaved Changes")
        msg.setText("There are unsaved files. What would you like to do?")
        msg.setStandardButtons(
            QMessageBox.StandardButton.Save |
            QMessageBox.StandardButton.Discard |
            QMessageBox.StandardButton.Cancel
        )
        msg.setDefaultButton(QMessageBox.StandardButton.Save)
        choice = msg.exec()

        if choice == QMessageBox.StandardButton.Save:
            save_all_files(self)
            event.accept()
        elif choice == QMessageBox.StandardButton.Discard:
            event.accept()
        else:
            event.ignore()


# -------------------------------
# App Entry Point
# -------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
