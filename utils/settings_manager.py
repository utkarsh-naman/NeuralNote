# import sqlite3
# import os

# SETTINGS_DB = os.path.join("config", "app_settings.db")
# # Ensure the config folder exists
# os.makedirs(os.path.dirname(SETTINGS_DB), exist_ok=True) 

# class SettingsManager:
#     def __init__(self):
#         self.conn = sqlite3.connect(SETTINGS_DB)
#         self.cursor = self.conn.cursor()
#         self._setup_table()

#     def _setup_table(self):
#         self.cursor.execute("""
#             CREATE TABLE IF NOT EXISTS settings (
#                 key TEXT PRIMARY KEY,
#                 value TEXT
#             )
#         """)
#         # Initialize 'nlp_enabled' setting if it doesn't exist
#         self.cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", 
#                             ('nlp_enabled', '0')) # Default: 0 (Off)
#         self.conn.commit()

#     def get_setting(self, key: str, default: str = None) -> str:
#         self.cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
#         result = self.cursor.fetchone()
#         return result[0] if result else default

#     def set_setting(self, key: str, value: str):
#         self.cursor.execute("""
#             INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)
#         """, (key, value))
#         self.conn.commit()
    
#     def close(self):
#         self.conn.close()

# # Global instance
# settings_manager = SettingsManager()


import sqlite3
import os

# 1. Define the database path
DB_FOLDER = "config"
SETTINGS_DB = os.path.join(DB_FOLDER, "../config/app_settings.db")

class SettingsManager:
    """Manages persistent application settings using a simple SQLite database."""

    def __init__(self):
        # Ensure the config folder exists before connecting
        os.makedirs(DB_FOLDER, exist_ok=True)
        self.conn = sqlite3.connect(SETTINGS_DB)
        self.cursor = self.conn.cursor()
        self._setup_table()

    def _setup_table(self):
        """Creates the settings table and initializes the 'nlp_enabled' key."""
        # The key stores the setting name (e.g., 'nlp_enabled')
        # The value stores the state ('1' for True, '0' for False)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        
        # Initialize 'nlp_enabled' setting if it doesn't exist (default: 0 / Off)
        self.cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", 
                            ('nlp_enabled', '0')) 
        self.conn.commit()

    def get_setting(self, key: str, default: str = '0') -> str:
        """Retrieves a setting value."""
        self.cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        result = self.cursor.fetchone()
        return result[0] if result else default

    def set_setting(self, key: str, value: str):
        """Saves or updates a setting value."""
        self.cursor.execute("""
            INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)
        """, (key, value))
        self.conn.commit()
    
    def close(self):
        """Closes the database connection."""
        self.conn.close()

# Global instance to be imported by main.py
settings_manager = SettingsManager()