import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QStatusBar, QLabel, QTabWidget, QWidget, QMenu, QMenuBar, QPushButton, QHBoxLayout, QToolButton
)

from PyQt6.QtGui import QFont, QIcon, QAction, QKeySequence, QTextCharFormat, QTextCursor
from PyQt6.QtCore import Qt, QTimer # 🌟 ADD QT.QTimer HERE



from ops.file.new_tab import create_new_tab
from ops.file.new_window import create_new_window
from ops.file.exit import exit_app
from ops.file.open import open_file
from ops.file.save import save_file, save_file_as, save_all_files
from ops.file.close_tab import close_tab
from ops.file.recent import show_recent_files_menu

from ops.edit.undo_redo import undo_action, redo_action
from ops.edit.delete_ops import delete_selected, delete_current_line
from ops.edit.select_ops import select_all
from ops.edit.cut import cut_text
from ops.edit.copy import copy_text
from ops.edit.paste import paste_text
from ops.edit.goto import goto_line

from ops.edit.find import FindReplaceWidget

from ui.custom_tab_bar import CustomTabBar



# NLPPPPPPPPPPPPPPPPPPPPPPPPMKBPPPPPPPPPPPPPPPP
from utils.settings_manager import settings_manager
from nlp.grammar_checker import GrammarChecker
from ui.custom_tab_bar import CustomTabBar      


# --- ADD IMPORTS ---
import ai.database as db
from ai.select_model import create_ai_menu
from ai.prompt_box import PromptDialog
# --- END ADD ---



class GrammarTextEdit(QTextEdit):
    """Subclassed QTextEdit to handle custom context menu and error storage."""
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.main_window = main_window
        self.grammar_errors = [] # Stores: (start_pos, end_pos, suggestion)

        # Re-implement the standard context menu handler
    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()

        # Find cursor position in the block (line)
        cursor = self.cursorForPosition(event.pos())
        block = cursor.block()
        position_in_block = cursor.position() - block.position()

        error_found = False
        suggestion = None
        start, end = -1, -1

        # Check if the click is within any highlighted error span
        for e_start, e_end, sugg in self.grammar_errors:
            if e_start <= position_in_block < e_end:
                error_found = True
                suggestion = sugg
                start, end = e_start, e_end
                break

        if error_found:
            menu.addSeparator()

            # Action 1: Accept suggestion
            accept_action = menu.addAction(f"Correct: '{suggestion}'")
            accept_action.triggered.connect(lambda: self.accept_grammar_suggestion(block, start, end, suggestion))

            # Action 2: Decline suggestion
            decline_action = menu.addAction("Ignore Correction")
            decline_action.triggered.connect(lambda: self.decline_grammar_suggestion(block, start, end))

        menu.exec(event.globalPos())

    def accept_grammar_suggestion(self, block, start, end, suggestion):
        """Applies the correction and removes the error highlight."""
        cursor = self.textCursor()
        abs_start_pos = block.position() + start
        abs_end_pos = block.position() + end

        cursor.setPosition(abs_start_pos)
        cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, abs_end_pos - abs_start_pos)

        # Replace the text
        cursor.insertText(suggestion)

        # Update error list and trigger re-highlight
        self.main_window._remove_grammar_error(start, end)
        self.main_window._apply_grammar_highlights(self)

    def decline_grammar_suggestion(self, block, start, end):
        """Removes the highlight without changing text."""
        self.main_window._remove_grammar_error(start, end)
        self.main_window._apply_grammar_highlights(self)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # --- ADD DB INIT ---
        db.init_db()
        # --- END ADD ---
        self.prompt_dialog = None

        self.setWindowTitle("NeuralNote")
        self.resize(1000, 700) 
        self.open_files = {} # To track file paths for saving

        self.settings = settings_manager
        self.grammar_checker = GrammarChecker()
        if self.settings.get_setting('nlp_enabled') == '1':
            self.grammar_checker.load_model()

        # 🌟 NEW: Debouncer/Throttler for live check (important for performance)
        self.check_timer = QTimer(self)
        self.check_timer.setSingleShot(True)
        self.check_timer.timeout.connect(self._check_current_line_for_grammar)



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
        self.find_widget = FindReplaceWidget(self)
        self._createMenuBar()
        self._createStatusBar()
        self._createTabs()
        self._updateStatusBar()

        

    def _mark_dirty(self, editor):
        index = self.tab_widget.indexOf(editor)
        if index == -1:
            return

        title = self.tab_widget.tabText(index)
        if not title.endswith("*"):
            self.tab_widget.setTabText(index, title + "*")

    def _createTabs(self):
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True) # Allow tabs to be closed
        self.tab_widget.setMovable(True)      # Allow tabs to be dragged


        custom_bar = CustomTabBar()
        self.tab_widget.setTabBar(custom_bar)
        self.tab_widget.setMovable(True)
        custom_bar.tabCloseRequested.connect(lambda i: close_tab(self, self.tab_widget, i))
        self.tab_widget.tabCloseRequested.connect(lambda i: close_tab(self, self.tab_widget, i))
        self.tab_widget.currentChanged.connect(custom_bar.updateAllTabIcons)
        self.tab_widget.currentChanged.connect(self._updateStatusBar)
        
        # -------------------------------------------------------------
        # 🎯 CONSOLIDATED: Create ONE tab using the custom editor and 
        # connect ALL necessary signals (dirty mark and NLP check)
        # -------------------------------------------------------------
        editor = create_new_tab(
            self.tab_widget, 
            self._updateStatusBar, 
            "Untitled",
            editor_class=GrammarTextEdit, # The custom editor subclass
            main_window=self # The self reference (MainWindow)
        )
        
        # Connect the 'dirty' marker (for saving)
        editor.textChanged.connect(lambda e=editor: self._mark_dirty(e)) 
        
        # Connect the NLP feature trigger (using the performance-throttled scheduler)
        editor.textChanged.connect(self._schedule_grammar_check)

        self.setCentralWidget(self.tab_widget)
    
    def _closeTab(self, index: int):
        widget = self.tab_widget.widget(index)
        
        if widget:
            self.tab_widget.removeTab(index)
            widget.deleteLater()

    # def current_editor(self) -> QTextEdit | None:
    #     widget = self.tab_widget.currentWidget()
    #     if isinstance(widget, QTextEdit):
    #         return widget
    #     return None

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
        file_menu.addSeparator()
        show_recent_files_menu(self, file_menu)
        
        file_menu.addSeparator()
        
        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        save_action.triggered.connect(lambda: save_file(self))
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save As...", self)
        save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_as_action.triggered.connect(lambda: save_file_as(self))
        file_menu.addAction(save_as_action)
        
        save_all_action = QAction("Save All", self)
        save_all_action.triggered.connect(lambda: save_all_files(self))
        file_menu.addAction(save_all_action)

        # --- ADD SEPARATOR AND EXIT ACTION ---
        file_menu.addSeparator()

        close_tab_action = QAction("Close Tab", self)
        close_tab_action.setShortcut(QKeySequence("Ctrl+W"))
        close_tab_action.triggered.connect(lambda: close_tab(self, self.tab_widget, self.tab_widget.currentIndex()))
        file_menu.addAction(close_tab_action)

        close_window_action = QAction("Close Window", self)
        close_window_action.setShortcut(QKeySequence("Ctrl+Shift+W"))
        close_window_action.triggered.connect(self.close)
        file_menu.addAction(close_window_action)


        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit) # Ctrl+Q
        exit_action.triggered.connect(exit_app)
        file_menu.addAction(exit_action)

        # ---------- EDIT MENU ----------
        edit_menu = menu_bar.addMenu("&Edit")

        # Undo / Redo
        undo_act = QAction("Undo", self)
        undo_act.setShortcut(QKeySequence.StandardKey.Undo)
        undo_act.triggered.connect(lambda: undo_action(self))
        edit_menu.addAction(undo_act)

        redo_act = QAction("Redo", self)
        redo_act.setShortcut(QKeySequence.StandardKey.Redo)
        redo_act.triggered.connect(lambda: redo_action(self))
        edit_menu.addAction(redo_act)

        edit_menu.addSeparator()

        cut_action = QAction("Cut", self)
        cut_action.setShortcut(QKeySequence.StandardKey.Cut) # Ctrl+X
        cut_action.triggered.connect(lambda: cut_text(self))
        edit_menu.addAction(cut_action)

        copy_action = QAction("Copy", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy) # Ctrl+C
        copy_action.triggered.connect(lambda: copy_text(self))
        edit_menu.addAction(copy_action)

        paste_action = QAction("Paste", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste) # Ctrl+V
        paste_action.triggered.connect(lambda: paste_text(self))
        edit_menu.addAction(paste_action)

        # Delete
        delete_sel_act = QAction("Delete Selection", self)
        delete_sel_act.setShortcut(QKeySequence("Del"))
        delete_sel_act.triggered.connect(lambda: delete_selected(self))
        edit_menu.addAction(delete_sel_act)

        # --- ADD THIS BLOCK ---
        find_action = QAction("Find/Replace...", self)
        find_action.setShortcut(QKeySequence.StandardKey.Find) # Ctrl+F
        find_action.triggered.connect(self.find_widget.show)
        edit_menu.addAction(find_action)
        # --- END ADD ---

        edit_menu.addSeparator()

        goto_action = QAction("Go to Line...", self)
        goto_action.setShortcut(QKeySequence("Ctrl+G")) # Ctrl+G
        goto_action.triggered.connect(lambda: goto_line(self))
        edit_menu.addAction(goto_action)

        delete_line_act = QAction("Delete Current Line", self)
        delete_line_act.setShortcut(QKeySequence("Ctrl+Shift+D"))
        delete_line_act.triggered.connect(lambda: delete_current_line(self))
        edit_menu.addAction(delete_line_act)

        edit_menu.addSeparator()

        # Select All
        select_all_act = QAction("Select All", self)
        select_all_act.setShortcut(QKeySequence.StandardKey.SelectAll)
        select_all_act.triggered.connect(lambda: select_all(self))
        edit_menu.addAction(select_all_act)

        # ... (existing menus: File, Edit)

        # ---------- SETTINGS MENU ----------
        # settings_menu = menu_bar.addMenu("&Settings")
        # --- ADD THIS BLOCK TO MOVE SETTINGS TO THE RIGHT ---
        
        # 1. Create a new QWidget container to live in the corner
        corner_container = QWidget(self)
        corner_layout = QHBoxLayout(corner_container)
        corner_layout.setContentsMargins(0, 0, 0, 0)
        corner_layout.setSpacing(0) # Pack buttons tightly
        
        # --- ADD PROMPT BUTTON (YELLOW CIRCLE) ---
        self.prompt_button = QPushButton("●")
        # Style the button to look like the image
        self.prompt_button.setStyleSheet("""
            QPushButton {
                color: #c2a042; /* Yellow */
                font-size: 20px;
                font-weight: bold;
                border: none;
                background: none;
                padding-top: -4px; /* Adjust vertical alignment */
            }
            QPushButton:hover {
                color: #d6b55d; /* Lighter yellow */
            }
            QPushButton:pressed {
                color: #a08021; /* Darker yellow */
            }
        """)
        self.prompt_button.setFixedSize(24, 24)
        self.prompt_button.setToolTip("Generate AI Content")
        self.prompt_button.clicked.connect(self.on_show_prompt_box)
        # Add the button to the corner layout
        corner_layout.addWidget(self.prompt_button)
        
        
        # 2. Create the AI Menu using our new function
        self.ai_menu = create_ai_menu(self)
        
        # 3. Create a ToolButton to host the AI Menu
        ai_button = QToolButton(self)
        ai_button.setText("AI")
        ai_button.setMenu(self.ai_menu)
        ai_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        # Style it to look like a flat menu bar item
        ai_button.setStyleSheet("QToolButton { border: none; padding: 0px 5px; } QToolButton::menu-indicator { image: none; }") 
        corner_layout.addWidget(ai_button)


        # 4. Create the Settings QMenu
        settings_menu = QMenu("&Settings", self)
        
        # 5. Add actions to the Settings menu
        nlp_toggle_action = QAction("Enable Grammar Check", self)
        nlp_toggle_action.setCheckable(True)

        # Set initial state from SQLite
        initial_state = self.settings.get_setting('nlp_enabled') == '1'
        nlp_toggle_action.setChecked(initial_state)

        nlp_toggle_action.triggered.connect(self.on_nlp_toggle)
        settings_menu.addAction(nlp_toggle_action)
    
        # 6. Create a ToolButton to host the Settings Menu
        settings_button = QToolButton(self)
        settings_button.setText("Settings")
        settings_button.setMenu(settings_menu)
        settings_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        # Style it to look like a flat menu bar item
        settings_button.setStyleSheet("QToolButton { border: none; padding: 0px 5px; } QToolButton::menu-indicator { image: none; }")
        corner_layout.addWidget(settings_button)
        
        # 7. Set the corner CONTAINER as the main bar's corner widget
        menu_bar.setCornerWidget(corner_container, Qt.Corner.TopRightCorner)


    def on_show_prompt_box(self):
        """Creates (if needed) and shows the PromptDialog."""
        if not self.prompt_dialog:
            self.prompt_dialog = PromptDialog(self)
            
        self.prompt_dialog.show()
        # Ensure it pops up on top
        self.prompt_dialog.activateWindow()
        self.prompt_dialog.raise_()

    def on_new_tab_action(self):
        # create_new_tab(self.tab_widget, self._updateStatusBar, "Untitled")
        editor = create_new_tab(self.tab_widget, self._updateStatusBar, "Untitled")
        editor.textChanged.connect(lambda e=editor: self._mark_dirty(e))

    def on_new_window_action(self):
        create_new_window(MainWindow)

    def closeEvent(self, event):
        """Prompt to save unsaved tabs before closing the window."""
        from PyQt6.QtWidgets import QMessageBox
        from ops.file.save import save_file, save_all_files

        unsaved_tabs = []
        for i in range(self.tab_widget.count()):
            title = self.tab_widget.tabText(i)
            if title.endswith("*"):
                unsaved_tabs.append(i)

        if not unsaved_tabs:
            event.accept()
            return

        msg = QMessageBox(self)
        msg.setWindowTitle("Unsaved Changes")
        msg.setText("There are unsaved files. What would you like to do?")
        msg.setStandardButtons(
            QMessageBox.StandardButton.Save |
            QMessageBox.StandardButton.Discard |
            QMessageBox.StandardButton.Cancel
        )
        msg.setDefaultButton(QMessageBox.StandardButton.Save)
        choice = msg.exec()

        if choice == QMessageBox.StandardButton.Save:
            save_all_files(self)
            event.accept()
        elif choice == QMessageBox.StandardButton.Discard:
            event.accept()
        else:
            event.ignore()


        if event.isAccepted():
            self.settings.close() # Close SQLite connection


    def on_open_file_action(self):
        open_file(self)
        editor = self.current_editor()
        if editor:
            editor.textChanged.connect(lambda e=editor: self._mark_dirty(e))

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


    # NLPPPPPPPPPPPPPPPPPPPPPPPPPPPMKBPPPPPPPPPPPPPPP
    # Inside MainWindow class

    def on_nlp_toggle(self, checked):
        """Toggles the NLP feature and loads/unloads the model."""
        state = '1' if checked else '0'
        self.settings.set_setting('nlp_enabled', state)

        if checked:
            self.grammar_checker.load_model()
        else:
            self.grammar_checker.unload_model()
            # Clear all highlights in the current editor immediately
            current_editor = self.current_editor()
            if current_editor and isinstance(current_editor, GrammarTextEdit):
                current_editor.grammar_errors = []
                current_editor.setExtraSelections([])


    def _schedule_grammar_check(self):
        """Uses a QTimer to delay the grammar check, preventing lag while typing."""
        if self.settings.get_setting('nlp_enabled') == '1':
            # Restart the timer. Check will run 500ms after the last keypress.
            self.check_timer.start(500) 


    def _check_current_line_for_grammar(self):
        """The core function that runs the NLP model on the current line."""
        current_editor = self.current_editor()

        if not current_editor or self.settings.get_setting('nlp_enabled') == '0':
            return

        cursor = current_editor.textCursor()
        current_block = cursor.block()
        line_text = current_block.text()

        if not line_text.strip():
            current_editor.grammar_errors = []
            self._apply_grammar_highlights(current_editor)
            return

        # 1. Get errors from NLP (using the Gramformer.get_edits method now)
        # Returns: (start_index, end_index, error_text, suggestion)
        errors = self.grammar_checker.check_line(line_text)

        # 2. Store error data on the editor instance for the context menu
        final_errors = []
        for edit_tuple in errors:
            try:
                # Manually unpack and cast everything to ensure no string remains in the index positions
                start_index = int(edit_tuple[0])
                end_index = int(edit_tuple[1])
                suggestion = str(edit_tuple[3]) # This is the suggestion text

                final_errors.append((start_index, end_index, suggestion))
            except Exception as e:
                # If the tuple is malformed, we simply skip the error
                continue

        current_editor.grammar_errors = final_errors

        # 3. Apply the visual highlights
        self._apply_grammar_highlights(current_editor)


    def _apply_grammar_highlights(self, editor: GrammarTextEdit):
        """Applies the yellow wave underline based on errors stored on the editor."""
        selections = []
        error_format = QTextCharFormat()
        error_format.setUnderlineStyle(QTextCharFormat.UnderlineStyle.WaveUnderline)
        error_format.setUnderlineColor(Qt.GlobalColor.yellow)

        current_block = editor.textCursor().block()

        # Iterate through stored errors and create selections
        for start_index, end_index, _ in editor.grammar_errors:
            selection = QTextEdit.ExtraSelection()
            selection.cursor = editor.textCursor()

            # Position the cursor for the selection within the current block
            abs_start_pos = current_block.position() + start_index

            selection.cursor.setPosition(abs_start_pos)
            selection.cursor.movePosition(
                QTextCursor.MoveOperation.Right, 
                QTextCursor.MoveMode.KeepAnchor, 
                end_index - start_index
            )
            selection.format = error_format
            selections.append(selection)

        # Apply the highlights
        editor.setExtraSelections(selections)


    def _remove_grammar_error(self, start, end):
        """Called by the CustomTextEditor to remove a specific error by span."""
        current_editor = self.current_editor()
        if not isinstance(current_editor, GrammarTextEdit):
            return

        # Filter out the error that matches the start/end indices
        new_errors = []
        for e_start, e_end, sugg in current_editor.grammar_errors:
            if not (e_start == start and e_end == end):
                new_errors.append((e_start, e_end, sugg))

        current_editor.grammar_errors = new_errors

    # Update current_editor to ensure it's the correct type for safety
    def current_editor(self) -> GrammarTextEdit | None:
        widget = self.tab_widget.currentWidget()
        if isinstance(widget, GrammarTextEdit):
            return widget
        return None





if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())