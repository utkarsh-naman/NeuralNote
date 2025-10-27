import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QStatusBar, QLabel, QTabWidget, QWidget
)
from PyQt6.QtGui import QFont, QIcon, QAction, QKeySequence
from PyQt6.QtCore import Qt

from ops.file.new_tab import create_new_tab
from ops.file.new_window import create_new_window
from ops.file.exit import exit_app
from ops.file.open import open_file
from ops.file.close_tab import close_tab

from ui.custom_tab_bar import CustomTabBar



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("NeuralNote")
        self.resize(1000, 700) 
        self.open_files = {} # To track file paths for saving
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
            QStatusBar::item { 
                border: none; /* Remove borders between status bar items */
            }
            QTabWidget::pane {
                border-top: 2px solid #3c3c3c;
            }
            QTabBar::tab {
                background: #3c3c3c;
                color: #f0f0f0;
                padding: 8px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                
                /* We must add padding-right here to make space
                   for our *programmatic* button */
                padding-right: 22px;
            }
            QTabBar::tab:selected {
                background: #2b2b2b;
            }
            
            /* --- QTabBar::close-button rules removed --- */
            /* All button logic is now in ui/custom_tab_bar.py */
            
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

    def _createTabs(self):
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True) # Allow tabs to be closed
        self.tab_widget.setMovable(True)      # Allow tabs to be dragged


        custom_bar = CustomTabBar()
        self.tab_widget.setTabBar(custom_bar)
        self.tab_widget.setMovable(True)
        custom_bar.tabCloseRequested.connect(self._closeTab)
        self.tab_widget.currentChanged.connect(custom_bar.updateAllTabIcons)
        self.tab_widget.currentChanged.connect(self._updateStatusBar)
        self.tab_widget.tabCloseRequested.connect(self._closeTab)
        create_new_tab(self.tab_widget, self._updateStatusBar, "Untitled")
        self.setCentralWidget(self.tab_widget)

    def _closeTab(self, index: int):
        widget = self.tab_widget.widget(index)
        
        if widget:
            self.tab_widget.removeTab(index)
            widget.deleteLater()

    def _createMenuBar(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("&File")
        new_tab_action = QAction("&New Tab", self)
        shortcuts = [
            QKeySequence.StandardKey.New,  # Ctrl+N (or Cmd+N on Mac)
            QKeySequence("Ctrl+T")         # Ctrl+T
        ]
        new_tab_action.setShortcuts(shortcuts) # Ctrl+N
        new_tab_action.triggered.connect(self.on_new_tab_action)

        
        file_menu.addAction(new_tab_action)

        # --- ADD NEW WINDOW ACTION ---
        new_window_action = QAction("New &Window", self)
        new_window_action.setShortcut(QKeySequence("Ctrl+Shift+N"))
        new_window_action.triggered.connect(self.on_new_window_action)
        file_menu.addAction(new_window_action)
        # --- END ADD ---


        open_action = QAction("Open", self)
        open_action.setShortcut(QKeySequence("Ctrl+O"))
        open_action.triggered.connect(self.on_open_file_action)
        file_menu.addAction(open_action)

        # --- ADD SEPARATOR AND EXIT ACTION ---
        file_menu.addSeparator()

        close_tab_action = QAction("Close Tab", self)
        close_tab_action.setShortcut(QKeySequence("Ctrl+W"))
        close_tab_action.triggered.connect(lambda: close_tab(self.tab_widget, self.tab_widget.currentIndex()))
        file_menu.addAction(close_tab_action)

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit) # Ctrl+Q
        exit_action.triggered.connect(exit_app)
        file_menu.addAction(exit_action)

        edit_menu = menu_bar.addMenu("&Edit")
    
    def on_new_tab_action(self):
        create_new_tab(self.tab_widget, self._updateStatusBar, "Untitled")

    def on_new_window_action(self):
        create_new_window(MainWindow)

    def on_open_file_action(self):
        open_file(self)

    def current_editor(self) -> QTextEdit | None:
        widget = self.tab_widget.currentWidget()
        if isinstance(widget, QTextEdit):
            return widget
        return None

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
            
            self.zoom_label.setText("100%")
            self.line_ending_label.setText("Windows (CRLF)")
            self.encoding_label.setText("UTF-8")
        
        else:
            # No tabs open, reset labels to default
            self.cursor_pos_label.setText("Ln 1, Col 1")
            self.char_count_label.setText("0 characters")
            self.zoom_label.setText("100%")
            self.line_ending_label.setText("Windows (CRLF)")
            self.encoding_label.setText("UTF-8")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())