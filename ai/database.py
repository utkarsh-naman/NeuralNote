# ai/database.py

import sqlite3
import os

DATABASE_FILE = "neuralnote_settings.db"

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database and creates tables if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Table for API Keys
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS api_keys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model_name TEXT NOT NULL,
        key_name TEXT NOT NULL,
        api_key TEXT NOT NULL
    );
    """)
    
    # Table for general settings
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    );
    """)
    
    conn.commit()
    conn.close()

# --- Settings Functions ---

def set_setting(key, value):
    """Saves or updates a setting in the settings table."""
    conn = get_db_connection()
    conn.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", 
        (key, value)
    )
    conn.commit()
    conn.close()

def get_setting(key, default=None):
    """Retrieves a setting from the settings table."""
    conn = get_db_connection()
    row = conn.execute(
        "SELECT value FROM settings WHERE key = ?", 
        (key,)
    ).fetchone()
    conn.close()
    return row['value'] if row else default

# --- API Key CRUD Functions ---

def add_api_key(model_name, key_name, api_key):
    """Adds a new API key to the database."""
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO api_keys (model_name, key_name, api_key) VALUES (?, ?, ?)",
        (model_name, key_name, api_key)
    )
    conn.commit()
    conn.close()

def update_api_key(key_id, new_name, new_key):
    """Updates an existing API key."""
    conn = get_db_connection()
    conn.execute(
        "UPDATE api_keys SET key_name = ?, api_key = ? WHERE id = ?",
        (new_name, new_key, key_id)
    )
    conn.commit()
    conn.close()

def delete_api_key(key_id):
    """Deletes an API key from the database."""
    conn = get_db_connection()
    conn.execute("DELETE FROM api_keys WHERE id = ?", (key_id,))
    conn.commit()
    conn.close()

def get_api_keys_by_model(model_name):
    """Retrieves all API keys for a specific model."""
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT id, key_name FROM api_keys WHERE model_name = ?",
        (model_name,)
    ).fetchall()
    conn.close()
    # Return as a list of (id, key_name) tuples
    return [(row['id'], row['key_name']) for row in rows]

def get_full_key(key_id):
    """Retrieves the full details for a single key (for editing)."""
    conn = get_db_connection()
    row = conn.execute(
        "SELECT key_name, api_key FROM api_keys WHERE id = ?",
        (key_id,)
    ).fetchone()
    conn.close()
    return (row['key_name'], row['api_key']) if row else (None, None)