import sys
import base64
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QTextEdit, QVBoxLayout,
    QWidget, QMenuBar, QMenu, QDialog, QLineEdit, QPushButton,
    QMessageBox, QFileDialog, QLabel, QRadioButton, QDialogButtonBox,
    QHBoxLayout, QToolBar, QSpacerItem, QSizePolicy
)
from PyQt6.QtGui import QAction, QKeySequence, QIcon, QFont, QPixmap
from PyQt6.QtCore import Qt, QSize

# Helper to create icons from base64 strings, now with padding correction.
def get_icon_from_base64(base64_string):
    """
    Converts a base64 encoded string to a QIcon, fixing padding if necessary.
    This makes it robust against common copy-paste errors.
    """
    # Strip any whitespace that might have been introduced
    base64_string = "".join(base64_string.split())
    
    # Add correct padding if it's missing
    missing_padding = len(base64_string) % 4
    if missing_padding:
        base64_string += '=' * (4 - missing_padding)
    
    try:
        pixmap = QPixmap()
        pixmap.loadFromData(base64.b64decode(base64_string))
        return QIcon(pixmap)
    except Exception as e:
        print(f"Error decoding base64 string: {e}")
        return QIcon() # Return an empty icon on failure


# Base64 encoded icon strings
AI_ICON_B64 = "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"
DROPDOWN_ICON_B64 = "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAACYSURBVHhe7dixCQAgEETR9196BoqASDS9KSPg251zd3d3d3d3d3d3d3d3d3d3959z/gAhQoQIESJEiBAhQoQIESJEiBAhQoQIESJEiBAhQoQIESJEiBAhQoQIESJEiBAhQoQIESJEiBAhQoQIESJEiBAhQoQIESJEiBD55wcY6f4A5XwAIUKECBEiRIgQIUKECBEiRIgQIfIHYoABR/gP2m4AAAAASUVORK5CYII="


class AIApiKeyDialog(QDialog):
    """Dialog to configure API keys for AI models."""
    def __init__(self, model_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Configure {model_name} API Key")
        self.setMinimumWidth(400)

        self.layout = QVBoxLayout(self)

        self.info_label = QLabel(f"Enter your API key for {model_name}:")
        self.layout.addWidget(self.info_label)

        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Paste your API key here")
        self.layout.addWidget(self.api_key_input)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def get_api_key(self):
        """Returns the entered API key."""
        return self.api_key_input.text()


class AIModelSelectionDialog(QDialog):
    """Dialog to select AI model and configure its API key."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select AI Model")
        self.selected_model = "Gemini" # Default

        layout = QVBoxLayout(self)

        self.gemini_button = QRadioButton("Gemini")
        self.gemini_button.setChecked(True)
        self.openai_button = QRadioButton("OpenAI")

        # Gemini Row
        gemini_layout = QHBoxLayout()
        gemini_layout.addWidget(self.gemini_button)
        gemini_layout.addStretch()
        edit_gemini_button = QPushButton(">")
        edit_gemini_button.setFixedSize(24, 24)
        edit_gemini_button.clicked.connect(lambda: self.configure_api_key("Gemini"))
        gemini_layout.addWidget(edit_gemini_button)

        # OpenAI Row
        openai_layout = QHBoxLayout()
        openai_layout.addWidget(self.openai_button)
        openai_layout.addStretch()
        edit_openai_button = QPushButton(">")
        edit_openai_button.setFixedSize(24, 24)
        edit_openai_button.clicked.connect(lambda: self.configure_api_key("OpenAI"))
        openai_layout.addWidget(edit_openai_button)

        layout.addLayout(gemini_layout)
        layout.addLayout(openai_layout)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        self.buttons.accepted.connect(self.accept)
        layout.addWidget(self.buttons)
        self.setLayout(layout)

    def configure_api_key(self, model_name):
        dialog = AIApiKeyDialog(model_name, self)
        if dialog.exec():
            api_key = dialog.get_api_key()
            if api_key:
                print(f"API Key for {model_name} set to: {api_key}") # In a real app, save this securely
                QMessageBox.information(self, "Success", f"API Key for {model_name} has been saved.")
            else:
                QMessageBox.warning(self, "Warning", "API Key cannot be empty.")

    def accept(self):
        if self.gemini_button.isChecked():
            self.selected_model = "Gemini"
        elif self.openai_button.isChecked():
            self.selected_model = "OpenAI"
        super().accept()


class AIPromptDialog(QDialog):
    """Dialog for user to enter a prompt and see the AI-generated text."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI Text Generation")
        self.setMinimumSize(500, 350)
        self.generated_text = ""

        layout = QVBoxLayout(self)
        prompt_label = QLabel("Enter your prompt:")
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("e.g., 'Write a python function to sort a list'")
        
        generate_button = QPushButton("Generate")
        generate_button.clicked.connect(self.generate_text)

        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setVisible(False)

        self.button_layout = QHBoxLayout()
        self.ignore_button = QPushButton("Ignore")
        self.ignore_button.clicked.connect(self.reject)
        self.copy_button = QPushButton("Copy")
        self.copy_button.clicked.connect(self.copy_text)
        self.insert_button = QPushButton("Insert")
        self.insert_button.clicked.connect(self.accept)
        
        self.button_layout.addWidget(self.ignore_button)
        self.button_layout.addWidget(self.copy_button)
        self.button_layout.addWidget(self.insert_button)
        for button in [self.ignore_button, self.copy_button, self.insert_button]:
            button.setVisible(False)

        layout.addWidget(prompt_label)
        layout.addWidget(self.prompt_input)
        layout.addWidget(generate_button)
        layout.addWidget(self.result_display)
        layout.addLayout(self.button_layout)
        self.setLayout(layout)

    def generate_text(self):
        """Placeholder for AI text generation logic."""
        prompt = self.prompt_input.toPlainText()
        if not prompt:
            QMessageBox.warning(self, "Empty Prompt", "Please enter a prompt to generate text.")
            return
            
        # --- MOCK AI RESPONSE ---
        # In a real app, you would make an API call here.
        self.generated_text = f"// AI-Generated code based on your prompt:\n// '{prompt}'\n\nfunction example() {{\n    console.log('Hello from AI!');\n}}\n"
        # --- END MOCK ---
        
        self.result_display.setText(self.generated_text)
        self.result_display.setVisible(True)
        for button in [self.ignore_button, self.copy_button, self.insert_button]:
            button.setVisible(True)

    def copy_text(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.generated_text)
        QMessageBox.information(self, "Copied", "Generated text copied to clipboard.")


class MainWindow(QMainWindow):
    """The main window of the text editor application."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NeuralNote: base version")
        self.setGeometry(100, 100, 900, 700)
        self.open_files = {} # To track file paths for saving

        self.setup_ui()
        self.create_menus()
        self.new_tab() # Start with one empty tab

    def setup_ui(self):
        """Set up the main UI components."""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Apply a modern stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QTextEdit {
                background-color: #272727;
                color: #f2f2f2;
                border: 1px solid #555;
                font-family: Consolas, 'Courier New', monospace;
                font-size: 14px;
            }
            QMenuBar {
                background-color: #272727;
                color: #f2f2f2;
            }
            QMenuBar::item:selected {
                background-color: #555;
            }
            QMenu {
                background-color: #272727;
                color: #f2f2f2;
                border: 1px solid #555;
            }
            QMenu::item:selected {
                background-color: #555;
            }
            QToolBar {
                background-color: #272727;
                border: none;
            }
            QPushButton {
                background-color: #555;
                color: #f2f2f2;
                border: 1px solid #666;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #666;
            }
            QPushButton:pressed {
                background-color: #777;
            }
            QTabWidget::pane {
                border: none;
            }
            QTabBar::tab {
                background: #272727;
                color: #f2f2f2;
                padding: 8px;
                border: 1px solid #555;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background: #2b2b2b;
            }
            QTabBar::tab:!selected {
                margin-top: 2px;
            }
            QDialog {
                background-color: #2b2b2b;
                color: #f2f2f2;
            }
            QLineEdit, QTextEdit {
                background-color: #272727;
                color: #f2f2f2;
                border: 1px solid #555;
            }
            QLabel, QRadioButton {
                color: #f2f2f2;
            }
        """)

        # Tab Widget for multiple documents
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.layout.addWidget(self.tabs)

    def create_menus(self):
        """Create the main menu bar and toolbar."""
        # --- Top-Left Menus ---
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu("&File")
        
        new_tab_action = QAction("New Tab", self)
        new_tab_action.setShortcut(QKeySequence("Ctrl+T"))
        new_tab_action.triggered.connect(self.new_tab)
        file_menu.addAction(new_tab_action)
        
        new_window_action = QAction("New Window", self)
        new_window_action.setShortcut(QKeySequence("Ctrl+Shift+N"))
        new_window_action.triggered.connect(lambda: MainWindow().show())
        file_menu.addAction(new_window_action)

        file_menu.addSeparator()

        open_action = QAction("Open...", self)
        open_action.setShortcut(QKeySequence("Ctrl+O"))
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        file_menu.addMenu("Open Recent") # Placeholder

        file_menu.addSeparator()
        
        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save As...", self)
        save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        save_all_action = QAction("Save All", self)
        save_all_action.triggered.connect(self.save_all_files)
        file_menu.addAction(save_all_action)

        file_menu.addSeparator()

        close_tab_action = QAction("Close Tab", self)
        close_tab_action.setShortcut(QKeySequence("Ctrl+W"))
        close_tab_action.triggered.connect(lambda: self.close_tab(self.tabs.currentIndex()))
        file_menu.addAction(close_tab_action)

        close_window_action = QAction("Close Window", self)
        close_window_action.setShortcut(QKeySequence("Ctrl+Shift+W"))
        close_window_action.triggered.connect(self.close)
        file_menu.addAction(close_window_action)
        
        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit Menu
        edit_menu = menu_bar.addMenu("&Edit")
        undo_action = QAction("Undo", self)
        undo_action.setShortcut(QKeySequence("Ctrl+Z"))
        undo_action.triggered.connect(lambda: self.current_editor().undo())
        edit_menu.addAction(undo_action)

        edit_menu.addSeparator()

        cut_action = QAction("Cut", self)
        cut_action.setShortcut(QKeySequence("Ctrl+X"))
        cut_action.triggered.connect(lambda: self.current_editor().cut())
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("Copy", self)
        copy_action.setShortcut(QKeySequence("Ctrl+C"))
        copy_action.triggered.connect(lambda: self.current_editor().copy())
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("Paste", self)
        paste_action.setShortcut(QKeySequence("Ctrl+V"))
        paste_action.triggered.connect(lambda: self.current_editor().paste())
        edit_menu.addAction(paste_action)

        edit_menu.addSeparator()
        
        find_action = QAction("Find...", self)
        find_action.setShortcut(QKeySequence("Ctrl+F"))
        edit_menu.addAction(find_action) # Placeholder
        replace_action = QAction("Replace...", self)
        replace_action.setShortcut(QKeySequence("Ctrl+H"))
        edit_menu.addAction(replace_action) # Placeholder

        edit_menu.addSeparator()

        select_all_action = QAction("Select All", self)
        select_all_action.setShortcut(QKeySequence("Ctrl+A"))
        select_all_action.triggered.connect(lambda: self.current_editor().selectAll())
        edit_menu.addAction(select_all_action)
        
        # --- Top-Right AI Controls ---
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)
        toolbar.setMovable(False)
        
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        toolbar.addWidget(spacer)

        self.ai_button = QPushButton()
        self.ai_button.setIcon(get_icon_from_base64(AI_ICON_B64))
        self.ai_button.setToolTip("Generate text with AI")
        self.ai_button.clicked.connect(self.open_ai_prompt)
        self.ai_button.setFlat(True)
        toolbar.addWidget(self.ai_button)

        self.ai_model_menu_button = QPushButton()
        self.ai_model_menu_button.setIcon(get_icon_from_base64(DROPDOWN_ICON_B64))
        self.ai_model_menu_button.setToolTip("Select AI Model")
        self.ai_model_menu_button.setFlat(True)
        self.ai_model_menu_button.clicked.connect(self.open_ai_model_selection)
        toolbar.addWidget(self.ai_model_menu_button)

    # --- Helper and Slot Functions ---

    def current_editor(self):
        """Returns the QTextEdit widget of the currently active tab."""
        if self.tabs.count() == 0:
            return None
        return self.tabs.currentWidget()

    def new_tab(self, checked=False, filename="Untitled"):
        """Creates a new tab with a text editor."""
        editor = QTextEdit()
        editor.setFont(QFont("Consolas", 12))
        index = self.tabs.addTab(editor, filename)
        self.tabs.setCurrentIndex(index)
        self.open_files[editor] = None # No file path associated yet

    def close_tab(self, index):
        """Closes the specified tab."""
        if self.tabs.count() == 0:
            return
        
        # If this is the last tab, close the window.
        if self.tabs.count() == 1:
            self.close()
            return
            
        widget = self.tabs.widget(index)
        if widget is not None:
            if widget in self.open_files:
                del self.open_files[widget]
            widget.deleteLater()
            self.tabs.removeTab(index)

    def open_file(self):
        """Opens a file and displays its content in a new tab."""
        filepath, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Text Files (*.txt);;Python Files (*.py)")
        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # If the current tab is empty and unsaved, use it. Otherwise, create a new one.
                editor = self.current_editor()
                if editor and not self.open_files.get(editor) and not editor.toPlainText():
                    index = self.tabs.currentIndex()
                    self.tabs.setTabText(index, filepath.split('/')[-1])
                else:
                    self.new_tab(filename=filepath.split('/')[-1])
                    editor = self.current_editor()

                editor.setText(content)
                self.open_files[editor] = filepath
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open file: {e}")

    def save_file(self):
        """Saves the current file. Opens 'Save As' if it's a new file."""
        editor = self.current_editor()
        if not editor: return

        filepath = self.open_files.get(editor)
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(editor.toPlainText())
                self.tabs.setTabText(self.tabs.currentIndex(), filepath.split('/')[-1])
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file: {e}")
        else:
            self.save_file_as()

    def save_file_as(self):
        """Saves the current file to a new location."""
        editor = self.current_editor()
        if not editor: return

        filepath, _ = QFileDialog.getSaveFileName(self, "Save File As", "", "All Files (*);;Text Files (*.txt);;Python Files (*.py)")
        if filepath:
            self.open_files[editor] = filepath
            self.save_file() # Call save_file to do the actual writing

    def save_all_files(self):
        """Saves all open files."""
        for i in range(self.tabs.count()):
            editor = self.tabs.widget(i)
            filepath = self.open_files.get(editor)
            if filepath:
                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(editor.toPlainText())
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Could not save file {filepath}: {e}")
            # Note: This simple implementation doesn't prompt "Save As" for untitled files.
        QMessageBox.information(self, "Success", "All opened files have been saved.")

    def open_ai_prompt(self):
        """Opens the AI prompt dialog."""
        editor = self.current_editor()
        if not editor:
            QMessageBox.warning(self, "No Tab", "Please open a tab before using the AI feature.")
            return
        
        dialog = AIPromptDialog(self)
        if dialog.exec():
            generated_text = dialog.generated_text
            editor.insertPlainText(generated_text)
            
    def open_ai_model_selection(self):
        """Opens the AI model selection dialog."""
        dialog = AIModelSelectionDialog(self)
        if dialog.exec():
            print(f"Active AI Model switched to: {dialog.selected_model}") # For debugging


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())