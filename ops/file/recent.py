import os
import sqlite3

from PyQt6.QtWidgets import QMenu, QMessageBox
from PyQt6.QtGui import QAction


DB_PATH = os.path.join("local_storage", "recentdb.db")


def init_recent_db():
    """Initialize the database if it doesn't exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS recent_files (
            filename TEXT NOT NULL,
            fullpath TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def add_recent_file(filename, fullpath):
    """Insert or update a recent file in the database, keeping only 10."""
    init_recent_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Remove if already exists (avoid duplicates)
    cur.execute("DELETE FROM recent_files WHERE fullpath = ?", (fullpath,))

    # Insert new record at top
    cur.execute("INSERT INTO recent_files (filename, fullpath) VALUES (?, ?)", (filename, fullpath))

    # Keep only latest 10
    cur.execute("""
        DELETE FROM recent_files 
        WHERE rowid NOT IN (
            SELECT rowid FROM recent_files ORDER BY rowid DESC LIMIT 10
        )
    """)

    conn.commit()
    conn.close()


def get_recent_files():
    """Fetch recent files (latest first)."""
    init_recent_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT filename, fullpath FROM recent_files ORDER BY rowid DESC LIMIT 10")
    rows = cur.fetchall()
    conn.close()
    return rows


def show_recent_files_menu(main_window, file_menu):
    """Add 'Recent Files' context submenu under File menu."""
    recent_menu = QMenu("Recent Files", main_window)
    recent_files = get_recent_files()

    if not recent_files:
        empty_action = QAction("(No recent files)", main_window)
        empty_action.setEnabled(False)
        recent_menu.addAction(empty_action)
    else:
        for filename, fullpath in recent_files:
            action = QAction(filename, main_window)
            action.setToolTip(fullpath)
            action.triggered.connect(lambda checked=False, path=fullpath: open_recent_file(main_window, path))
            recent_menu.addAction(action)

    file_menu.addMenu(recent_menu)


def open_recent_file(main_window, fullpath):
    """Open a file from the recents list."""
    from ops.file.open import open_file
    import os

    if not os.path.exists(fullpath):
        QMessageBox.warning(main_window, "File Missing", f"The file does not exist:\n{fullpath}")
        return

    open_file(main_window, fullpath)
