from PyQt6.QtWidgets import (
    QDialog, QWidget, QTextEdit, QPushButton, QLabel, QVBoxLayout, 
    QHBoxLayout, QStackedWidget, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import ai.database as db
from ai.select_model import ApiKeyManagerDialog
import ai.gemini.g_call as g_call
import ai.openai.o_call as o_call

# --- Worker thread for non-blocking API calls ---
class GenerationWorker(QThread):
    """Runs the API call in a separate thread to avoid freezing the UI."""
    # Signal emits (generated_text, error_message)
    generation_complete = pyqtSignal(str, str)

    def __init__(self, model_name, api_key, prompt):
        super().__init__()
        self.model_name = model_name
        self.api_key = api_key
        self.prompt = prompt

    def run(self):
        text, err = None, None
        try:
            if self.model_name == "Gemini":
                text, err = g_call.generate_text(self.api_key, self.prompt)
            else: # OpenAI
                text, err = o_call.generate_text(self.api_key, self.prompt)
            
            self.generation_complete.emit(text or "", err or "")
            
        except Exception as e:
            self.generation_complete.emit("", f"An unexpected error occurred: {str(e)}")


# --- Main Prompt Dialog (Groups 10 & 11) ---
class PromptDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent # Store reference to MainWindow
        self.generated_text = ""
        self.worker_thread = None

        self.setWindowTitle("Generate Text")
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setModal(False)
        self.setStyleSheet(PROMPT_STYLESHEET)
        
        # Main Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        # Prompt/Result Text Edit
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setMinimumSize(450, 150)
        layout.addWidget(self.prompt_edit)

        # Close button (the 'x' in the corner)
        self.close_btn = QPushButton("X", self)
        self.close_btn.setObjectName("CloseButton")
        self.close_btn.clicked.connect(self.reject)
        
        # --- Button Stack (Generate vs Insert/Discard) ---
        self.button_stack = QStackedWidget()
        layout.addWidget(self.button_stack)

        # Page 1: Generate
        generate_widget = QWidget()
        generate_layout = QHBoxLayout(generate_widget)
        generate_layout.setContentsMargins(0,0,0,0)
        
        self.generate_btn = QPushButton("Generate")
        self.generate_btn.setObjectName("GenerateButton")
        self.generate_btn.clicked.connect(self.on_generate)
        
        self.warning_label = QLabel("AI generated content may be incorrect")
        self.warning_label.setObjectName("WarningLabel")
        
        generate_layout.addWidget(self.generate_btn)
        generate_layout.addWidget(self.warning_label)
        generate_layout.addStretch()
        
        self.button_stack.addWidget(generate_widget)

        # Page 2: Insert/Discard
        review_widget = QWidget()
        review_layout = QHBoxLayout(review_widget)
        review_layout.setContentsMargins(0,0,0,0)

        self.insert_btn = QPushButton("Insert")
        self.insert_btn.setObjectName("InsertButton")
        self.insert_btn.clicked.connect(self.on_insert)

        self.discard_btn = QPushButton("Discard")
        self.discard_btn.setObjectName("DiscardButton")
        self.discard_btn.clicked.connect(self.reject) # Discard just closes
        
        review_layout.addWidget(self.insert_btn)
        review_layout.addWidget(self.discard_btn)
        review_layout.addWidget(self.warning_label) # Re-use label
        review_layout.addStretch()

        self.button_stack.addWidget(review_widget)
        # --- End Button Stack ---

        self.reset_to_prompt_state()

    def resizeEvent(self, event):
        """Keep the 'x' button in the top right corner."""
        super().resizeEvent(event)
        self.close_btn.move(self.width() - 35, 8)

    def showEvent(self, event):
        """Called every time the dialog is shown."""
        super().showEvent(event)
        self.reset_to_prompt_state()
        
        # Move to be centered on the main window
        if self.main_window:
            mw_geom = self.main_window.geometry()
            self_geom = self.frameGeometry()
            center_point = mw_geom.center()
            self_geom.moveCenter(center_point)
            self.move(self_geom.topLeft())

    def reset_to_prompt_state(self):
        """Resets the dialog to the initial 'prompting' state."""
        self.generated_text = ""
        self.prompt_edit.clear()
        self.prompt_edit.setPlaceholderText("What would you like to generate? How about \"Chicken Noodles soup recipe\".")
        self.prompt_edit.setReadOnly(False)
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("Generate")
        self.button_stack.setCurrentIndex(0) # Show 'Generate' button

    def on_generate(self):
        prompt = self.prompt_edit.toPlainText().strip()
        if not prompt:
            return

        model_name = db.get_setting('selected_model', 'Gemini')
        key_id = db.get_setting(f'active_{model_name}_key_id')
        api_key = None

        if key_id:
            name, key = db.get_full_key(key_id)
            api_key = key

        if not api_key:
            QMessageBox.warning(
                self, 
                "API Key Missing", 
                f"No active {model_name} API key found.\n"
                f"Please add or select a key in the API manager."
            )
            # Open the key manager for them
            self.open_key_manager(model_name)
            return
        
        # Set loading state
        self.generate_btn.setText("Generating...")
        self.generate_btn.setEnabled(False)
        self.prompt_edit.setReadOnly(True)

        # Run API call in a separate thread
        self.worker_thread = GenerationWorker(model_name, api_key, prompt)
        self.worker_thread.generation_complete.connect(self.on_generation_complete)
        self.worker_thread.start()

    def on_generation_complete(self, text, error):
        if error:
            # On error, reset to prompt state but show the error
            self.reset_to_prompt_state()
            self.prompt_edit.setText(f"Error: {error}\n\nPlease check your key or try again.")
            return

        self.generated_text = text
        self.prompt_edit.setText(text) # Show generated text
        self.prompt_edit.setReadOnly(True)
        self.button_stack.setCurrentIndex(1) # Show 'Insert/Discard'

    def on_insert(self):
        editor = self.main_window.current_editor()
        if editor and self.generated_text:
            editor.insertPlainText(self.generated_text)
        
        self.accept() # Closes the dialog

    def open_key_manager(self, model_name):
        dialog = ApiKeyManagerDialog(model_name, self.main_window)
        dialog.exec()


# --- Stylesheet for the Prompt Box ---
PROMPT_STYLESHEET = """
    QDialog {
        background-color: #2b2b2b;
        color: #f0f0f0;
        border: 1px solid #555;
        border-radius: 8px;
    }
    
    QTextEdit {
        background-color: #3c3c3c;
        color: #f0f0f0;
        border: none;
        border-radius: 4px;
        font-size: 11pt;
        padding: 8px;
    }
    
    QLabel#WarningLabel {
        color: #aaa;
        font-size: 9pt;
        padding-left: 10px;
    }

    QPushButton {
        color: #f0f0f0;
        border: 1px solid #666;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 10pt;
    }
    QPushButton:hover {
        background-color: #666;
    }

    QPushButton#GenerateButton {
        background-color: #c2a042; /* Yellow */
        color: #000;
        font-weight: bold;
    }
    QPushButton#GenerateButton:hover {
        background-color: #d6b55d;
    }
    QPushButton#GenerateButton:disabled {
        background-color: #555;
        color: #999;
    }
    
    QPushButton#InsertButton {
        background-color: #4a8c4a; /* Green */
        font-weight: bold;
    }
    QPushButton#InsertButton:hover {
        background-color: #5aa05a;
    }

    QPushButton#DiscardButton {
        background-color: #a95e38; /* Orange */
    }
    QPushButton#DiscardButton:hover {
        background-color: #c07040;
    }
    
    QPushButton#CloseButton {
        font-family: "Consolas", "Courier New", monospace;
        font-weight: bold;
        font-size: 12pt;
        border: none;
        background: none;
        color: #999;
        min-width: 20px;
        max-width: 20px;
        padding: 0px;
    }
    QPushButton#CloseButton:hover {
        color: #f0f0f0;
    }
"""
