from PyQt6.QtWidgets import QApplication

def exit_app():
    """ 
    Quits the entire application.
    This is necessary for multi-window applications.
    """
    QApplication.instance().quit()
