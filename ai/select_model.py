# ai/select_model.py

from PyQt6.QtWidgets import (
    QWidget, QMenu, QDialog, QLabel, QRadioButton, QPushButton, QLineEdit,
    QVBoxLayout, QHBoxLayout, QWidgetAction, QButtonGroup, QMessageBox,
    QFormLayout
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QAction, QActionGroup # <-- This import was from your last fix
import ai.database as db

# --- Stylesheet for Dark UI ---
MENU_STYLESHEET = """
    QMenu {
        background-color: #3c3c3c;
        color: #f0f0f0;
        border: 1px solid #555;
    }
    QMenu::item:selected {
        background-color: #555;
    }
    QMenu::separator {
        height: 1px;
        background: #555;
        margin-left: 5px;
        margin-right: 5px;
    }
    
    /* --- MODIFIED: Style QDialogs instead of QWidget --- */
    QDialog#ApiKeyManagerDialog, QDialog#AddApiKeyDialog {
        background-color: #3c3c3c;
        color: #f0f0f0;
    }
    
    /* Give the manager dialog a default size */
    QDialog#ApiKeyManagerDialog {
        min-width: 350px;
    }
    
    QLabel, QRadioButton {
        color: #f0f0f0;
        font-size: 10pt;
    }
    
    QPushButton {
        background-color: #555;
        color: #f0f0f0;
        border: 1px solid #666;
        padding: 5px 10px;
        border-radius: 4px;
    }
    QPushButton:hover {
        background-color: #666;
    }
    QPushButton#DeleteButton {
        background-color: #8c3b3b;
    }
    QPushButton#DeleteButton:hover {
        background-color: #a04a4a;
    }
    QPushButton#SelectButton, QPushButton#SaveButton {
        background-color: #4a8c4a;
    }
    QPushButton#SelectButton:hover, QPushButton#SaveButton:hover {
        background-color: #5aa05a;
    }
    
    QLineEdit {
        background-color: #2b2b2b;
        color: #f0f0f0;
        border: 1px solid #555;
        padding: 4px;
        border-radius: 4px;
    }
"""

# --- Add/Edit API Key Dialog (Group 9.png) ---
# (This class is mostly unchanged, but we ensure its ID is set for styling)
class AddApiKeyDialog(QDialog):
    """Dialog for adding or editing an API key."""
    key_saved = pyqtSignal()

    def __init__(self, model_name, key_id=None, parent=None):
        super().__init__(parent)
        self.model_name = model_name
        self.key_id = key_id
        
        # --- CHANGED: Set object name for styling ---
        self.setObjectName("AddApiKeyDialog") 
        self.setWindowTitle(f"Add New {model_name} API Key")
        self.setStyleSheet(MENU_STYLESHEET)
        
        # ... (rest of the __init__ is identical) ...
        
        # Create widgets
        self.name_label = QLabel("Enter API Key Name")
        self.name_input = QLineEdit()
        self.key_label = QLabel("Enter API Key")
        self.key_input = QLineEdit()
        
        self.save_btn = QPushButton("Save")
        self.save_btn.setObjectName("SaveButton")
        self.discard_btn = QPushButton("Discard")
        
        # Populate fields if editing
        if self.key_id:
            self.setWindowTitle(f"Edit {model_name} API Key")
            name, key = db.get_full_key(self.key_id)
            if name is not None:
                self.name_input.setText(name)
                self.key_input.setText(key)

        # Layout
        layout = QFormLayout(self)
        layout.addRow(self.name_label, self.name_input)
        layout.addRow(self.key_label, self.key_input)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.discard_btn)
        layout.addRow(button_layout)
        
        # Signals
        self.save_btn.clicked.connect(self.on_save)
        self.discard_btn.clicked.connect(self.reject)

    def on_save(self):
        key_name = self.name_input.text().strip()
        api_key = self.key_input.text().strip()
        
        if not key_name or not api_key:
            QMessageBox.warning(self, "Missing Information", "Both fields are required.")
            return
            
        if self.key_id:
            db.update_api_key(self.key_id, key_name, api_key)
        else:
            db.add_api_key(self.model_name, key_name, api_key)
            
        self.key_saved.emit()
        self.accept()


# --- API Key Manager Dialog (Group 8.png) ---
# --- MAJOR CHANGE: This is now a QDialog, not a QWidget ---
class ApiKeyManagerDialog(QDialog):
    """Custom DIALOG for the API key selection menu."""
    
    def __init__(self, model_name, parent=None):
        super().__init__(parent)
        self.model_name = model_name
        self.button_group = QButtonGroup(self)
        
        # --- CHANGED: Setup as a Dialog ---
        self.setObjectName("ApiKeyManagerDialog")
        self.setWindowTitle(f"{model_name} API Key Manager")
        self.setStyleSheet(MENU_STYLESHEET)
        # --- END CHANGE ---
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        
        # + Add New Key button
        self.add_key_btn = QPushButton(f"+ Add New {model_name} API Key")
        main_layout.addWidget(self.add_key_btn)
        
        # Layout for the list of keys
        self.keys_list_layout = QVBoxLayout()
        self.keys_list_layout.setSpacing(5)
        main_layout.addLayout(self.keys_list_layout)
        
        main_layout.addStretch()
        
        # Select / Cancel buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.select_btn = QPushButton("Select")
        self.select_btn.setObjectName("SelectButton")
        self.cancel_btn = QPushButton("Cancel")
        button_layout.addWidget(self.select_btn)
        button_layout.addWidget(self.cancel_btn)
        main_layout.addLayout(button_layout)
        
        # Populate the list
        self.populate_keys()
        
        # Signals
        self.add_key_btn.clicked.connect(self.on_add_key)
        self.select_btn.clicked.connect(self.on_select)
        # --- CHANGED: Connect to dialog's reject() slot ---
        self.cancel_btn.clicked.connect(self.reject)

    def populate_keys(self):
        """Clears and repopulates the list of API keys."""
        # Clear existing key widgets
        while self.keys_list_layout.count():
            child = self.keys_list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        # Get active key
        active_key_id = db.get_setting(f'active_{self.model_name}_key_id')
                
        # Get keys from DB
        keys = db.get_api_keys_by_model(self.model_name)
        
        for key_id, key_name in keys:
            # Create a widget for each key row
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0,0,0,0)
            
            radio_btn = QRadioButton(key_name)
            radio_btn.setProperty("key_id", key_id)
            self.button_group.addButton(radio_btn)
            
            if active_key_id and int(active_key_id) == key_id:
                radio_btn.setChecked(True)
            
            edit_btn = QPushButton("Edit")
            delete_btn = QPushButton("Delete")
            delete_btn.setObjectName("DeleteButton")
            
            # Connect signals
            # --- CHANGED: Pass 'self' (the dialog) as parent ---
            edit_btn.clicked.connect(lambda _, kid=key_id: self.on_edit_key(kid))
            delete_btn.clicked.connect(lambda _, kid=key_id, kname=key_name: self.on_delete_key(kid, kname))
            
            row_layout.addWidget(radio_btn)
            row_layout.addStretch()
            row_layout.addWidget(edit_btn)
            row_layout.addWidget(delete_btn)
            
            self.keys_list_layout.addWidget(row_widget)

    def on_add_key(self):
        # --- CHANGED: Pass 'self' (the dialog) as parent ---
        dialog = AddApiKeyDialog(self.model_name, parent=self)
        dialog.key_saved.connect(self.populate_keys)
        dialog.exec()

    def on_edit_key(self, key_id):
        # --- CHANGED: Pass 'self' (the dialog) as parent ---
        dialog = AddApiKeyDialog(self.model_name, key_id=key_id, parent=self)
        dialog.key_saved.connect(self.populate_keys)
        dialog.exec()

    def on_delete_key(self, key_id, key_name):
        reply = QMessageBox.warning(
            self,
            "Delete Key",
            f"Are you sure you want to delete '{key_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            db.delete_api_key(key_id)
            self.populate_keys()

    def on_select(self):
        checked_btn = self.button_group.checkedButton()
        if checked_btn:
            key_id = checked_btn.property("key_id")
            db.set_setting(f'active_{self.model_name}_key_id', str(key_id))
            # Also set this as the globally selected model
            db.set_setting('selected_model', self.model_name)
        
        # --- CHANGED: Connect to dialog's accept() slot ---
        self.accept()


# --- Main Menu Creation Function ---
# --- MAJOR CHANGE: This function no longer creates submenus ---
def create_ai_menu(parent):
    """Creates the main 'AI' menu."""
    ai_menu = QMenu("AI", parent)
    ai_menu.setStyleSheet(MENU_STYLESHEET)

    # 1. Title Label
    title_label = QLabel("  Choose AI model")
    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title_action = QWidgetAction(ai_menu)
    title_action.setDefaultWidget(title_label)
    ai_menu.addAction(title_action)

    # 2. Model Selection Radio Buttons (for selecting the *active* model)
    model_group = QActionGroup(ai_menu)
    model_group.setExclusive(True)
    
    gemini_action = QAction("Gemini", ai_menu, checkable=True)
    openai_action = QAction("OpenAI", ai_menu, checkable=True)
    
    model_group.addAction(gemini_action)
    model_group.addAction(openai_action)
    
    ai_menu.addAction(gemini_action)
    ai_menu.addAction(openai_action)
    
    # Set checked state from DB
    selected_model = db.get_setting('selected_model', 'Gemini')
    if selected_model == 'Gemini':
        gemini_action.setChecked(True)
    else:
        openai_action.setChecked(True)
        
    # Connect signals to save selection
    gemini_action.triggered.connect(lambda: db.set_setting('selected_model', 'Gemini'))
    openai_action.triggered.connect(lambda: db.set_setting('selected_model', 'OpenAI'))

    # --- CHANGED: REMOVED SUBMENU CREATION ---
    # (The QWidgetAction and ApiKeyManagerWidget logic is gone)

    # --- ADDED: Actions to OPEN the dialogs ---
    ai_menu.addSeparator()
    
    manage_gemini_action = QAction("Manage Gemini Keys...", ai_menu)
    manage_openai_action = QAction("Manage OpenAI Keys...", ai_menu)
    
    ai_menu.addAction(manage_gemini_action)
    ai_menu.addAction(manage_openai_action)

    # Helper function to open the dialog
    def open_api_manager(model_name):
        # 'parent' is the MainWindow, which was passed into create_ai_menu
        dialog = ApiKeyManagerDialog(model_name, parent)
        dialog.exec() # Opens the dialog modally
    
    # Connect the new actions
    manage_gemini_action.triggered.connect(lambda: open_api_manager("Gemini"))
    manage_openai_action.triggered.connect(lambda: open_api_manager("OpenAI"))
    # --- END CHANGE ---


    # 4. Close Button
    ai_menu.addSeparator()
    close_action = QAction("close", ai_menu)
    close_action.triggered.connect(ai_menu.close)
    ai_menu.addAction(close_action)
    
    return ai_menu