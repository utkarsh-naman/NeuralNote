"""
Operation for creating a new application window.
"""

# This list will hold references to all open windows
# to prevent them from being garbage-collected.
open_windows = []

def create_new_window(main_window_class):
    """
    Creates and shows a new instance of the MainWindow.
    
    :param main_window_class: The actual MainWindow class from main.py
    """
    # Create a new window instance
    new_win = main_window_class()
    
    # Store a reference to it
    open_windows.append(new_win)
    
    # Show the new window
    new_win.show()
    
    # When the window is closed (destroyed), remove it from our list
    # This uses a lambda with a default argument to capture the *current*
    # value of new_win, preventing scope issues.
    new_win.destroyed.connect(lambda win=new_win: open_windows.remove(win) if win in open_windows else None)
