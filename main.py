import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QStatusBar, QLabel, QTabWidget, QWidget
)
# --- ADD THESE IMPORTS ---
from PyQt6.QtGui import QFont, QIcon, QAction, QKeySequence
# --- MODIFIED IMPORT ---
from PyQt6.QtCore import Qt
# Import our new function
from ops.file.new_tab import create_new_tab
# --- END IMPORTS ---
from ui.custom_tab_bar import CustomTabBar
class MainWindow(QMainWindow):
    """
    Main application window for NeuralNote.
    
    Inherits from QMainWindow to provide a standard application skeleton
    with menu bar, status bar, and central widget.
    """
    def __init__(self):
        super().__init__()

        # --- Window Properties ---
        self.setWindowTitle("NeuralNote")
        self.resize(1000, 700) 
        
        # --- Theme (Corrected) ---
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

        # --- Create UI Components ---
        # 1. Create the menu bar
        self._createMenuBar()
        # 2. Create the status bar AND its labels first
        self._createStatusBar()
        # 3. NOW create the tabs, which will connect signals to the status bar
        self._createTabs()
        # 4. Call this once at the end to set the initial state correctly
        self._updateStatusBar()

    def _createTabs(self):
        """
        Create the central QTabWidget for holding text editors.
        """
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True) # Allow tabs to be closed
        self.tab_widget.setMovable(True)      # Allow tabs to be dragged


        # Set custom tab bar
        custom_bar = CustomTabBar()
        self.tab_widget.setTabBar(custom_bar)
        self.tab_widget.setMovable(True)
        # --- Signal Connections for Tabs ---
        custom_bar.tabCloseRequested.connect(self._closeTab)
        self.tab_widget.currentChanged.connect(custom_bar.updateAllTabIcons)
        # When user switches tabs, update status bar
        self.tab_widget.currentChanged.connect(self._updateStatusBar)
        
        # When user clicks 'x' on a tab
        # This connection *IS* correct and will work once
        # the QSS conflict is removed.
        self.tab_widget.tabCloseRequested.connect(self._closeTab)

        # --- MODIFIED LINE ---
        # Create the first tab using our new imported function
        create_new_tab(self.tab_widget, self._updateStatusBar, "Untitled")
        # --- END MODIFICATION ---

        # Set the tab widget as the central content
        self.setCentralWidget(self.tab_widget)

    def _closeTab(self, index: int):
        """
        Closes the tab at the given index.
        (We'll add "do you want to save?" logic here later)
        """
        # Get the widget (QTextEdit) in the tab
        widget = self.tab_widget.widget(index)
        
        if widget:
            # Remove the tab from the tab widget
            self.tab_widget.removeTab(index)
            # Delete the widget to free up memory
            widget.deleteLater()

    def _createMenuBar(self):
        """
        Create the main menu bar (File, Edit, View).
        """
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("&File")
        # --- ADD NEW TAB ACTION ---
        new_tab_action = QAction("&New Tab", self)
        new_tab_action.setShortcut(QKeySequence.StandardKey.New) # Ctrl+N
        new_tab_action.triggered.connect(self.on_new_tab_action)
        file_menu.addAction(new_tab_action)
        # --- END ADD ---

        edit_menu = menu_bar.addMenu("&Edit")
        view_menu = menu_bar.addMenu("&View")
    
    def on_new_tab_action(self):
        """
        Slot that is called when the 'New Tab' menu action is triggered.
        """
        create_new_tab(self.tab_widget, self._updateStatusBar, "Untitled")

    def _createStatusBar(self):
        """
        Create the status bar and store labels as instance attributes.
        """
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)

        # Create labels and store them
        self.cursor_pos_label = QLabel("Ln 1, Col 1")
        self.char_count_label = QLabel("0 characters")
        self.zoom_label = QLabel("100%")
        self.line_ending_label = QLabel("Windows (CRLF)")
        self.encoding_label = QLabel("UTF-8")

        # Add widgets to the status bar
        status_bar.addPermanentWidget(self.cursor_pos_label)
        status_bar.addPermanentWidget(self.char_count_label)
        status_bar.addPermanentWidget(self.zoom_label)
        status_bar.addPermanentWidget(self.line_ending_label)
        status_bar.addPermanentWidget(self.encoding_label)

    def _updateStatusBar(self):
        """
        Slot to update status bar labels based on the current editor's state.
        """
        # Get the currently active text editor
        current_editor = self.tab_widget.currentWidget()
        
        # Check if it's a QTextEdit (it might be None if all tabs are closed)
        if isinstance(current_editor, QTextEdit):
            # --- Get Cursor Position ---
            cursor = current_editor.textCursor()
            line = cursor.blockNumber() + 1
            col = cursor.columnNumber() + 1
            self.cursor_pos_label.setText(f"Ln {line}, Col {col}")
            
            # --- Get Character Count ---
            char_count = len(current_editor.toPlainText())
            self.char_count_label.setText(f"{char_count} characters")
            
            # --- Update other labels (for now, they are static) ---
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


# --- Main Application Execution ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

