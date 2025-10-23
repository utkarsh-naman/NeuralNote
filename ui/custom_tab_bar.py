# from PyQt6.QtWidgets import QTabBar
# from PyQt6.QtCore import Qt

# class CustomTabBar(QTabBar):
#     def tabInserted(self, index: int):
#         super().tabInserted(index)
#         self.updateTabIcon(index)

#     def tabRemoved(self, index: int):
#         super().tabRemoved(index)
#         self.updateAllTabIcons()

#     def tabChanged(self, index: int):
#         self.updateAllTabIcons()

#     def updateAllTabIcons(self):
#         for i in range(self.count()):
#             self.updateTabIcon(i)

#     def updateTabIcon(self, index: int):
        
#         if index == self.currentIndex():
#             # Selected tab: show cross2.svg
#             self.setTabButton(index, QTabBar.ButtonPosition.RightSide, None)
#             self.setTabButton(index, QTabBar.ButtonPosition.RightSide, self._createCloseButton("assets/cross2.svg"))
#         else:
#             # Unselected tab: show dot.svg
#             self.setTabButton(index, QTabBar.ButtonPosition.RightSide, None)
#             self.setTabButton(index, QTabBar.ButtonPosition.RightSide, self._createCloseButton("assets/dot.svg"))

#     def _createCloseButton(self, icon_path):
#         from PyQt6.QtWidgets import QToolButton
#         from PyQt6.QtGui import QIcon
#         btn = QToolButton()
#         btn.setIcon(QIcon(icon_path))
#         btn.setAutoRaise(True)
#         btn.setCursor(Qt.CursorShape.PointingHandCursor)

#         btn.clicked.connect(lambda: self.tabCloseRequested.emit(index))
#         # Change icon on hover
#         btn.enterEvent = lambda event, b=btn: b.setIcon(QIcon("assets/cross2.svg"))
#         btn.leaveEvent = lambda event, b=btn, p=icon_path: b.setIcon(QIcon(p))
#         return btn



from PyQt6.QtWidgets import QTabBar, QToolButton
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

class CustomTabBar(QTabBar):
    """
    A custom tab bar that programmatically controls the close button
    icon based on tab selection and hover state.
    This logic is based on the user's implementation.
    """
    def tabInserted(self, index: int):
        super().tabInserted(index)
        self.updateTabIcon(index)

    def tabRemoved(self, index: int):
        super().tabRemoved(index)
        self.updateAllTabIcons()

    def tabChanged(self, index: int):
        """
        Slot for when the selected tab changes.
        We must update all icons.
        """
        self.updateAllTabIcons()

    def updateAllTabIcons(self):
        """Updates the icon for every tab."""
        for i in range(self.count()):
            self.updateTabIcon(i)

    def updateTabIcon(self, index: int):
        """
        Sets the correct close button (dot or cross) for the tab
        at the given index based on whether it is selected.
        This re-creates the button each time to ensure all
        signals and icons are correct.
        """
        # Ensure index is still valid
        if index < 0 or index >= self.count():
            return
            
        if index == self.currentIndex():
            # Selected tab: show cross2.svg
            self.setTabButton(index, QTabBar.ButtonPosition.RightSide, None) # Clear old button
            # --- FIX ---
            # Pass the 'index' to the creation method
            self.setTabButton(index, QTabBar.ButtonPosition.RightSide, self._createCloseButton("assets/cross2.svg", index))
            # --- END FIX ---
        else:
            # Unselected tab: show dot.svg
            self.setTabButton(index, QTabBar.ButtonPosition.RightSide, None) # Clear old button
            # --- FIX ---
            # Pass the 'index' to the creation method
            self.setTabButton(index, QTabBar.ButtonPosition.RightSide, self._createCloseButton("assets/dot.svg", index))
            # --- END FIX ---

    def _createCloseButton(self, icon_path, index):
        """
        Creates a new QToolButton with the correct icon and signals connected.
        
        Args:
            icon_path (str): The "resting" (non-hover) icon for this button.
            index (int): The current tab index this button belongs to.
        """
        btn = QToolButton()
        btn.setIcon(QIcon(icon_path))
        btn.setAutoRaise(True)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)

        # --- FIX ---
        # The 'index' is now correctly captured by the lambda
        # from the method's arguments.
        btn.clicked.connect(lambda: self.tabCloseRequested.emit(index))
        # --- END FIX ---
        
        # --- This is YOUR hover logic, which works correctly ---
        # On hover, always show the cross
        btn.enterEvent = lambda event, b=btn: b.setIcon(QIcon("assets/cross2.svg"))
        
        # On leave, revert to the original icon path
        btn.leaveEvent = lambda event, b=btn, p=icon_path: b.setIcon(QIcon(p))
        
        return btn

