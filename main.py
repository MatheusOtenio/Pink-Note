import sys
import os
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt, QFile, QTextStream

from presentation.main_window import MainWindow
from shared.utils.logger import Logger
from shared.constants import APP_NAME, APP_VERSION

# Set up high DPI scaling
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

def exception_hook(exc_type, exc_value, exc_traceback):
    """Custom exception hook to log unhandled exceptions.
    
    Args:
        exc_type: Exception type
        exc_value: Exception value
        exc_traceback: Exception traceback
    """
    # Log the exception
    logger = Logger.get_instance()
    logger.error(f"Unhandled exception: {exc_value}\n{''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))}")
    
    # Format the traceback
    tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    tb_text = ''.join(tb_lines)
    
    # Show error message
    QMessageBox.critical(
        None,
        "Application Error",
        f"An unexpected error occurred:\n\n{exc_value}\n\n"
        f"Please report this error with the following information:\n\n{tb_text}"
    )
    
    # Call the original exception hook
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

def main():
    """Main application entry point."""
    # Set up exception hook
    sys.excepthook = exception_hook
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    
    # Load application stylesheet
    style_file = QFile(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'style.qss'))
    if style_file.exists():
        style_file.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(style_file)
        app.setStyleSheet(stream.readAll())
        style_file.close()
    
    # Create main window
    window = MainWindow()
    window.show()
    
    # Run application
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())