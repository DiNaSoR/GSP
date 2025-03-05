#!/usr/bin/env python3
"""
Game Settings Editor - A modern, user-friendly editor for game configuration files
"""

import sys
import os
import platform
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, QTimer

from main import IniEditorApp

def show_exception_box(error_msg):
    """Display a formatted error message box for uncaught exceptions"""
    error_box = QMessageBox()
    error_box.setIcon(QMessageBox.Icon.Critical)
    error_box.setWindowTitle("Application Error")
    error_box.setText("A critical error has occurred:")
    error_box.setInformativeText(error_msg)
    error_box.setDetailedText(traceback.format_exc())
    error_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    error_box.exec()

def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler to show a friendly message box"""
    if issubclass(exc_type, KeyboardInterrupt):
        # Let the default handler handle Ctrl+C
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
        
    error_msg = f"{exc_type.__name__}: {exc_value}"
    show_exception_box(error_msg)

def main():
    """Main application entry point"""
    # Set up exception handling
    sys.excepthook = handle_exception
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Game Settings Editor")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Gaming Tools")
    
    # Set app icon if available
    app_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(app_dir, 'styles', 'icon.png')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Check for high DPI display and enable accordingly
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Create and show splash screen
    splash_path = os.path.join(app_dir, 'styles', 'splash.png')
    if os.path.exists(splash_path):
        splash_pixmap = QPixmap(splash_path)
        splash = QSplashScreen(splash_pixmap)
        splash.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | 
                             Qt.WindowType.SplashScreen)
        splash.show()
        app.processEvents()
    else:
        splash = None
    
    # Create main window
    main_window = IniEditorApp()
    
    # Show main window and close splash after delay
    if splash:
        # Give it a slight delay to make the splash visible
        QTimer.singleShot(1500, lambda: (main_window.show(), splash.close()))
    else:
        main_window.show()
    
    # Start the application event loop
    return app.exec()

if __name__ == "__main__":
    sys.exit(main()) 