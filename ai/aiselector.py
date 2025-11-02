import sqlite3
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QRadioButton, 
    QPushButton, QLineEdit, QLabel, QMessageBox, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt

# --- Database Manager Class ---

class APIKeyManager:
    """Handles local database operations for storing API keys."""
    def __init__(self, db_name="api_keys.db"):
        self.db_name = db_name
        self._create_tables()
        self.selected_keys = {"gemini": None, "openai": None} # Tracks the currently selected key name (e.g., "Work Key")
        # NEW: Store the currently active model (e.g., "gemini" or "openai")
        self._selected_model = "gemini" 

    def _get_connection(self):
        return sqlite3.connect(self.db_name)

    def _create_tables(self):
        """Creates the 'gemini' and 'openai' tables if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gemini (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                api_key TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS openai (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                api_key TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    # --- NEW MODEL PROPERTIES ---
    @property
    def selected_model(self):
        """Getter for the currently selected model."""
        return self._selected_model

    @selected_model.setter
    def selected_model(self, model: str):
        """Setter for the currently selected model."""
        model = model.lower()
        if model in ["gemini", "openai"]:
            self._selected_model = model
    # --- END NEW MODEL PROPERTIES ---

    def add_key(self, model: str, name: str, key: str) -> bool:
        """Adds a new API key to the specified model's table."""
        model = model.lower()
        if model not in ["gemini", "openai"]:
            return False

        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(f"INSERT INTO {model} (name, api_key) VALUES (?, ?)", (name, key))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            QMessageBox.warning(None, "Error", f"An API key with the name '{name}' already exists for {model}.")
            return False
        finally:
            conn.close()

    def get_keys(self, model: str) -> list[tuple]:
        """Retrieves all stored keys (id, name, api_key) for a model."""
        model = model.lower()
        if model not in ["gemini", "openai"]:
            return []
        
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT id, name, api_key FROM {model}")
        keys = cursor.fetchall()
        conn.close()
        return keys

    def get_selected_key_value(self, model: str) -> str | None:
        """Returns the actual API key string for the currently selected key name."""
        model = model.lower()
        key_name = self.selected_keys.get(model)
        if not key_name:
            return None
        
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT api_key FROM {model} WHERE name = ?", (key_name,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    def set_selected_key(self, model: str, key_name: str):
        """Sets the name of the API key currently selected for a model."""
        self.selected_keys[model.lower()] = key_name

# --- Dialogs for API Key Selection and Addition ---
# (AddKeyDialog and SelectKeyDialog remain unchanged)

class AddKeyDialog(QDialog):
    """Dialog to add a new API key name and value."""
    def __init__(self, model: str, manager: APIKeyManager, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Add New {model.upper()} API Key")
        self.model = model
        self.manager = manager
        self.setGeometry(100, 100, 400, 150)
        
        layout = QVBoxLayout(self)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter API Key Name (e.g., 'Work Key')")
        
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Enter API Key Value")
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        layout.addWidget(QLabel("Key Name:"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("API Key Value:"))
        layout.addWidget(self.key_input)
        
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        save_button.clicked.connect(self.save_key)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def save_key(self):
        name = self.name_input.text().strip()
        key = self.key_input.text().strip()
        
        if not name or not key:
            QMessageBox.warning(self, "Input Error", "Both Key Name and API Key Value must be provided.")
            return

        if self.manager.add_key(self.model, name, key):
            self.accept()
            
class SelectKeyDialog(QDialog):
    """Dialog to select an existing API key or open the 'Add New' dialog."""
    def __init__(self, model: str, manager: APIKeyManager, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Select {model.upper()} API Key")
        self.model = model
        self.manager = manager
        self.selected_key_name = None
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout(self)
        
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.list_widget.itemClicked.connect(self._update_selection)
        layout.addWidget(self.list_widget)
        
        # Add buttons
        button_layout = QHBoxLayout()
        add_new_button = QPushButton("Add New API Key")
        select_button = QPushButton("Select")
        cancel_button = QPushButton("Cancel")
        
        add_new_button.clicked.connect(self._add_new_key)
        select_button.clicked.connect(self._select_key)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(add_new_button)
        button_layout.addStretch(1)
        button_layout.addWidget(select_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        self.load_keys()
        self._select_current_key()

    def load_keys(self):
        """Populates the list widget with saved key names."""
        self.list_widget.clear()
        keys = self.manager.get_keys(self.model)
        for _, name, _ in keys:
            item = QListWidgetItem(name)
            self.list_widget.addItem(item)
            
    def _select_current_key(self):
        """Highlights the key currently selected in the main app."""
        current_name = self.manager.selected_keys.get(self.model)
        if current_name:
            items = self.list_widget.findItems(current_name, Qt.MatchFlag.MatchExactly)
            if items:
                items[0].setSelected(True)
                self.list_widget.setCurrentItem(items[0])

    def _update_selection(self, item):
        self.selected_key_name = item.text()

    def _add_new_key(self):
        dialog = AddKeyDialog(self.model, self.manager, self)
        if dialog.exec():
            self.load_keys() # Refresh the list after adding a new key
            
    def _select_key(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Selection Error", "Please select an API key or add a new one.")
            return

        self.selected_key_name = selected_items[0].text()
        self.manager.set_selected_key(self.model, self.selected_key_name)
        self.accept()

# --- Main AI Selector Dialog ---

class AISelectorDialog(QDialog):
    """Main dialog to select the AI model and configure API keys."""
    def __init__(self, manager: APIKeyManager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI Model and API Key Selector")
        self.manager = manager
        # Removed self.selected_model = None; it now reads from self.manager
        self.setGeometry(100, 100, 300, 150)
        
        layout = QVBoxLayout(self)
        
        # Model Selection Group
        model_group = QGroupBox("Select AI Model")
        model_layout = QVBoxLayout()
        
        self.gemini_radio = QRadioButton("Gemini")
        self.openai_radio = QRadioButton("OpenAI")
        
        model_layout.addWidget(self.gemini_radio)
        model_layout.addWidget(self.openai_radio)
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)

        # API Key Buttons
        button_layout = QHBoxLayout()
        self.gemini_api_button = QPushButton("Configure Gemini API >")
        self.openai_api_button = QPushButton("Configure OpenAI API >")
        
        button_layout.addWidget(self.gemini_api_button)
        button_layout.addWidget(self.openai_api_button)
        layout.addLayout(button_layout)
        
        # OK/Cancel buttons
        ok_button = QPushButton("Close")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)
        
        # Initial state based on current selection (if any)
        self._update_ui_with_selection()

        # Connect signals
        # UPDATED: Use the setter method on the manager
        self.gemini_radio.toggled.connect(lambda: self._set_selected_model("gemini"))
        self.openai_radio.toggled.connect(lambda: self._set_selected_model("openai"))
        self.gemini_api_button.clicked.connect(lambda: self._open_select_key_dialog("gemini"))
        self.openai_api_button.clicked.connect(lambda: self._open_select_key_dialog("openai"))
        
    def _update_ui_with_selection(self):
        """Updates the button text and checks the appropriate radio button."""
        gemini_key = self.manager.selected_keys["gemini"]
        openai_key = self.manager.selected_keys["openai"]
        
        if gemini_key:
            self.gemini_api_button.setText(f"Gemini API: {gemini_key} >")
        else:
            self.gemini_api_button.setText("Configure Gemini API >")
            
        if openai_key:
            self.openai_api_button.setText(f"OpenAI API: {openai_key} >")
        else:
            self.openai_api_button.setText("Configure OpenAI API >")
            
        # FIX: Check the radio button based on the manager's persistent value
        current_model = self.manager.selected_model
        if current_model == "gemini":
            self.gemini_radio.setChecked(True)
        elif current_model == "openai":
            self.openai_radio.setChecked(True)

    def _set_selected_model(self, model: str):
        if self.sender().isChecked():
            # FIX: Set the selected model persistently in the manager
            self.manager.selected_model = model
            
    def _open_select_key_dialog(self, model: str):
        dialog = SelectKeyDialog(model, self.manager, self)
        if dialog.exec():
            # Update the button text after selection
            self._update_ui_with_selection()
            
class AIPromptDialog(QDialog):
    """Dialog for the AI button functionality (step 4)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI Prompt")
        self.generated_text = ""
        self.setGeometry(100, 100, 500, 400)

        layout = QVBoxLayout(self)

        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Enter your AI prompt here...")
        layout.addWidget(QLabel("Prompt:"))
        layout.addWidget(self.prompt_input)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("AI generated text will appear here...")
        layout.addWidget(QLabel("AI Output:"))
        layout.addWidget(self.output_text)

        button_layout = QHBoxLayout()
        generate_button = QPushButton("Generate")
        insert_button = QPushButton("Insert Text")
        cancel_button = QPushButton("Cancel")

        generate_button.clicked.connect(self._generate_text)
        insert_button.clicked.connect(self._insert_text)
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(generate_button)
        button_layout.addStretch(1)
        button_layout.addWidget(insert_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def _generate_text(self):
        # Access the MainWindow object (which is the parent) to get the manager
        main_window = self.parent()
        
        # Placeholder for AI generation logic
        prompt = self.prompt_input.toPlainText()
        if not prompt:
            self.output_text.setText("Please enter a prompt.")
            return

        # FIX: Access the selected_model from the manager property
        selected_model = main_window.api_key_manager.selected_model
        
        # Retrieve the key name for the currently selected model
        selected_key_name = main_window.api_key_manager.selected_keys.get(selected_model)
        
        if not selected_key_name:
            QMessageBox.warning(self, "No Key", f"Please select an API key for {selected_model.upper()} first.")
            return

        self.output_text.setText(f"--- Calling {selected_model.upper()} with key: {selected_key_name} ---\nPrompt: {prompt}\n\n[Simulated AI Response: This is the generated text based on your prompt.]")


    def _insert_text(self):
        if not self.output_text.toPlainText() or self.output_text.toPlainText().startswith("--- Calling"):
            QMessageBox.warning(self, "No Output", "Please generate AI text first.")
            return
            
        self.generated_text = self.output_text.toPlainText()
        self.accept()