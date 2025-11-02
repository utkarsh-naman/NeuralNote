from PyQt6.QtWidgets import QTextEdit, QMenu, QApplication
from PyQt6.QtGui import QTextCharFormat, QColor, QTextCursor
from PyQt6.QtCore import Qt

class CustomTextEditor(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.grammar_errors = {} # Stores error data for the context menu: {(start_pos, end_pos): suggestion, ...}
        
    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        
        # 1. Check if a grammar error is right-clicked
        cursor = self.cursorForPosition(event.pos())
        block = cursor.block()
        position_in_block = cursor.position() - block.position()
        
        # Check against all stored error spans for this block
        error_found = False
        suggestion = None
        for (start, end), sugg in self.grammar_errors.items():
            if start <= position_in_block < end:
                error_found = True
                suggestion = sugg
                break

        if error_found and suggestion:
            menu.addSeparator()
            
            # Add the suggestion action
            accept_action = menu.addAction(f"Correct: '{suggestion}'")
            accept_action.triggered.connect(lambda: self.accept_grammar_suggestion(block, start, end, suggestion))
            
            # Add the decline action
            decline_action = menu.addAction("Ignore/Decline Correction")
            decline_action.triggered.connect(lambda: self.decline_grammar_suggestion(block, start, end))
            
        menu.exec(event.globalPos())

    def accept_grammar_suggestion(self, block, start, end, suggestion):
        """Replaces the error text with the suggestion and removes the highlight."""
        cursor = self.textCursor()
        # Select the error span
        cursor.setPosition(block.position() + start)
        cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, end - start)
        
        # Replace the text
        cursor.insertText(suggestion)
        
        # Remove the error from the storage (and thus the highlight on next refresh)
        if (start, end) in self.grammar_errors:
            del self.grammar_errors[(start, end)]
            self.parent().parent()._check_current_line_for_grammar() # Re-highlight the line/document
        
        
    def decline_grammar_suggestion(self, block, start, end):
        """Removes the highlight without changing text."""
        if (start, end) in self.grammar_errors:
            del self.grammar_errors[(start, end)]
            self.parent().parent()._check_current_line_for_grammar() # Re-highlight the line/document

    # You must also implement a method to store and apply ExtraSelections (the highlights) 
    # using self.setExtraSelections() which is called after a grammar check.
    # The `self.grammar_errors` dictionary will be essential here.
    # The complexity is in ensuring the Main Window's logic interacts with this custom editor's state.