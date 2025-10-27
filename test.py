import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QStatusBar, QLabel, QTabWidget, QWidget
)
from PyQt6.QtGui import QFont, QIcon, QAction, QKeySequence
from PyQt6.QtCore import Qt

from ops.file.new_tab import create_new_tab
from ops.file.new_window import create_new_window
from ops.file.exit import exit_app
# --- Import the refactored open_file ---
from ops.file.open import open_file 

from ui.custom_tab_bar import CustomTabBar

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("NeuralNote")
        self.resize(1000, 700) 
        
        # --- ADD STATE TO TRACK OPEN FILES ---
        # This maps QTextEdit widgets to their filepaths
        self.open_files = {}
        # --- END ADD ---
        
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
        self.tab_widget.setTabsClosable(True)

        custom_bar = CustomTabBar()
        self.tab_widget.setTabBar(custom_bar)
        self.tab_widget.setMovable(True)
        
        # Connect signals
        custom_bar.tabCloseRequested.connect(self._closeTab)
        self.tab_widget.currentChanged.connect(custom_bar.updateAllTabIcons)
        self.tab_widget.currentChanged.connect(self._updateStatusBar)
        
        # Create the first tab
        create_new_tab(self.tab_widget, self._updateStatusBar, "Untitled")
        self.setCentralWidget(self.tab_widget)

    def _closeTab(self, index: int):
        widget = self.tab_widget.widget(index)
        
        if widget:
            # --- REMOVE FILE FROM TRACKING ---
            if widget in self.open_files:
                del self.open_files[widget]
            # --- END ADD ---
            
            self.tab_widget.removeTab(index)
            widget.deleteLater()

    def _createMenuBar(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("&File")
        
        # --- New Tab Action ---
        new_tab_action = QAction("&New Tab", self)
        shortcuts = [
            QKeySequence.StandardKey.New,  # Ctrl+N
            QKeySequence("Ctrl+T")         # Ctrl+T
        ]
        new_tab_action.setShortcuts(shortcuts) 
        new_tab_action.triggered.connect(self.on_new_tab_action)
        file_menu.addAction(new_tab_action)

        # --- New Window Action ---
        new_window_action = QAction("New &Window", self)
        new_window_action.setShortcut(QKeySequence("Ctrl+Shift+N"))
        new_window_action.triggered.connect(self.on_new_window_action)
        file_menu.addAction(new_window_action)

        # --- ADD OPEN ACTION ---
        open_action = QAction("&Open...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open) # Ctrl+O
        # Connect to the new slot
        open_action.triggered.connect(self.on_open_file_action)
        file_menu.addAction(open_action)
        # --- END ADD ---

        # --- Separator and Exit ---
        file_menu.addSeparator()
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit) # Ctrl+Q
        exit_action.triggered.connect(exit_app)
        file_menu.addAction(exit_action)

        edit_menu = menu_bar.addMenu("&Edit")
        # view_menu = menu_bar.addMenu("&View")
    
    def on_new_tab_action(self):
        create_new_tab(self.tab_widget, self._updateStatusBar, "Untitled")

    def on_new_window_action(self):
        create_new_window(MainWindow)

    # --- ADD THIS SLOT ---
    def on_open_file_action(self):
        """
        Slot to handle the 'Open' menu action.
        Calls the imported open_file function.
        """
        # Pass the MainWindow instance (self) to the function
        open_file(self)
    # --- END ADD ---
    
    # --- ADD THIS HELPER METHOD ---
    def current_editor(self) -> QTextEdit | None:
        """Helper to get the current text editor widget."""
        widget = self.tab_widget.currentWidget()
        if isinstance(widget, QTextEdit):
            return widget
        return None
    # --- END ADD ---

    def _createStatusBar(self):
        # ... (no changes here) ...
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
        # ... (no changes here) ...
        current_editor = self.current_editor() # Use new helper
        if current_editor:
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
            self.cursor_pos_label.setText("Ln 1, Col 1")
            self.char_count_label.setText("0 characters")
            self.zoom_label.setText("100%")
            self.line_ending_label.setText("Windows (CRLF)")
            self.encoding_label.setText("UTF-8")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Don't quit when a window is closed
    app.setQuitOnLastWindowClosed(False)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

