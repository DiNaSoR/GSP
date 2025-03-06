import sys
import os
import json
import configparser
import re
import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QLabel,
    QDoubleSpinBox, QSpinBox, QCheckBox, QLineEdit, QComboBox, QFileDialog,
    QMessageBox, QVBoxLayout, QHBoxLayout, QPushButton, 
    QScrollArea, QSplitter, QToolBar, QStatusBar, QFrame,
    QGridLayout, QSizePolicy, QStyle, QToolButton, QListWidget, QListWidgetItem
)
from PyQt6.QtGui import QFont, QAction, QColor, QPalette, QCursor
from PyQt6.QtCore import Qt, QSize

from modules.module_loader import ModuleLoader
from modules.generic_module import GenericModule

class IniEditorApp(QMainWindow):
    """Main application window for the INI Editor"""
    
    def __init__(self):
        super().__init__()
        self.module_loader = ModuleLoader()
        self.current_module = None
        self.current_file_path = None
        self.settings_data = {}
        self.ui_elements = {}
        self.edited = False
        self.dark_mode = True  # Always dark mode
        
        # Initialize configparser for app settings
        self.app_settings = configparser.ConfigParser()
        self.settings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app_settings.ini')
        self.load_app_settings()
        
        # Setup dark theme
        self.apply_dark_theme()
        
        # Apply stylesheet
        self.load_stylesheet()
        
        self.initUI()
    
    def load_app_settings(self):
        """Load application settings from config file"""
        # Create default settings if file doesn't exist
        if not os.path.exists(self.settings_file):
            self.app_settings['General'] = {
                'last_directory': '',
                'window_width': '1200',
                'window_height': '800',
                'save_position': 'True'
            }
            with open(self.settings_file, 'w') as f:
                self.app_settings.write(f)
        else:
            self.app_settings.read(self.settings_file)
    
    def save_app_settings(self):
        """Save application settings to config file"""
        # Update current settings
        if 'General' not in self.app_settings:
            self.app_settings['General'] = {}
            
        self.app_settings['General']['window_width'] = str(self.width())
        self.app_settings['General']['window_height'] = str(self.height())
        
        if self.app_settings.getboolean('General', 'save_position', fallback=True):
            pos = self.pos()
            self.app_settings['General']['pos_x'] = str(pos.x())
            self.app_settings['General']['pos_y'] = str(pos.y())
        
        with open(self.settings_file, 'w') as f:
            self.app_settings.write(f)
    
    def apply_dark_theme(self):
        """Apply dark theme to application"""
        dark_palette = QPalette()
        
        # Set dark color palette
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        
        self.setPalette(dark_palette)
    
    def recreateToolBar(self):
        """Recreate the toolbar with updated icons"""
        # Store current button states
        save_enabled = False
        export_enabled = False
        import_enabled = False
        close_file_enabled = False
        
        # Check if buttons exist and get their states
        if hasattr(self, 'save_action'):
            save_enabled = self.save_action.isEnabled()
        if hasattr(self, 'export_action'):
            export_enabled = self.export_action.isEnabled()
        if hasattr(self, 'import_action'):
            import_enabled = self.import_action.isEnabled()
        if hasattr(self, 'close_file_action'):
            close_file_enabled = self.close_file_action.isEnabled()
        
        # Remove existing toolbar
        for toolbar in self.findChildren(QToolBar):
            self.removeToolBar(toolbar)
        
        # Create new toolbar
        self.setupToolbar()
        
        # Restore button states
        if hasattr(self, 'save_action'):
            self.save_action.setEnabled(save_enabled)
        if hasattr(self, 'export_action'):
            self.export_action.setEnabled(export_enabled)
        if hasattr(self, 'import_action'):
            self.import_action.setEnabled(import_enabled)
        if hasattr(self, 'close_file_action'):
            self.close_file_action.setEnabled(close_file_enabled)
    
    def load_stylesheet(self):
        """Load or create application stylesheet"""
        style_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'styles')
        style_file = os.path.join(style_dir, 'dark_style.css')
        
        # Create styles directory if it doesn't exist
        if not os.path.exists(style_dir):
            os.makedirs(style_dir)
        
        # Create stylesheet if it doesn't exist
        if not os.path.exists(style_file):
            self.create_default_stylesheet(style_file)
        
        # Apply stylesheet
        try:
            with open(style_file, 'r') as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Error loading stylesheet: {str(e)}")
            # Create and apply default stylesheet if loading fails
            self.create_default_stylesheet(style_file)
            with open(style_file, 'r') as f:
                self.setStyleSheet(f.read())
    
    def create_default_stylesheet(self, style_file):
        """Create default stylesheet file"""
        # Common styles for all themes
        common_style = """
            QTabBar::tab {
                padding: 8px 12px;
                margin-right: 2px;
            }
            
            QTabWidget::pane {
                border-top: 1px solid palette(mid);
                padding: 5px;
            }
            
            QPushButton {
                padding: 6px 12px;
                border-radius: 4px;
                min-width: 80px;
            }
            
            QPushButton:hover {
                background-color: palette(highlight);
                color: palette(highlighted-text);
            }
            
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                padding: 5px;
                border-radius: 4px;
                border: 1px solid #cccccc;
                min-height: 20px;
            }
            
            QToolBar {
                border: none;
                spacing: 10px;
                padding: 5px;
            }
            
            QToolButton {
                padding: 4px;
                border-radius: 4px;
            }
            
            QToolButton:hover {
                background-color: palette(highlight);
                color: palette(highlighted-text);
            }
            
            QScrollArea {
                border: none;
            }
            
            QLabel {
                padding: 2px;
            }
            
            #headerWidget {
                margin-bottom: 10px;
                border-radius: 5px;
            }
        """
        
        # Dark theme styles
        dark_style = """
            QTabBar::tab {
                background-color: #333333;
                color: #ffffff;
                border: 1px solid #555555;
            }
            
            QTabBar::tab:selected {
                background-color: #444444;
                border-bottom: none;
            }
            
            QTabWidget::pane {
                border: 1px solid #555555;
            }
            
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
            }
            
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
            
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                background-color: #333333;
                color: #ffffff;
                border: 1px solid #555555;
            }
            
            QToolBar {
                background-color: #333333;
            }
            
            QStatusBar {
                background-color: #333333;
                color: #ffffff;
            }
            
            #headerWidget {
                background-color: #2980b9;
            }
        """
        
        # Write stylesheet to file
        try:
            with open(style_file, 'w') as f:
                f.write(common_style + dark_style)
        except Exception as e:
            print(f"Error creating stylesheet: {str(e)}")
    
    def initUI(self):
        # Set window properties
        self.setWindowTitle("Game Settings Editor")
        self.setWindowIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        
        # Apply window size from settings
        try:
            width = int(self.app_settings.get('General', 'window_width', fallback='1200'))
            height = int(self.app_settings.get('General', 'window_height', fallback='800'))
            self.resize(width, height)
            
            # Apply position if saved
            if self.app_settings.getboolean('General', 'save_position', fallback=True):
                pos_x = int(self.app_settings.get('General', 'pos_x', fallback='100'))
                pos_y = int(self.app_settings.get('General', 'pos_y', fallback='100'))
                self.move(pos_x, pos_y)
        except (ValueError, configparser.Error):
            self.setMinimumSize(1200, 800)
        
        # Create central widget with main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(10)
        
        # Setup toolbar and menu
        self.setupToolbar()
        self.setupMenu()
        
        # Create splash screen for initial state
        self.createSplashScreen()
        
        # Setup status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - No file loaded")
    
    def setupMenu(self):
        """Setup the application menu bar"""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&File")
        
        # Use existing open action if available
        if not hasattr(self, 'open_action'):
            self.open_action = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon), "&Open INI", self)
            self.open_action.setShortcut("Ctrl+O")
            self.open_action.setStatusTip("Open an INI file")
            self.open_action.triggered.connect(self.openFile)
        file_menu.addAction(self.open_action)
        
        # Create save action if it doesn't exist
        if not hasattr(self, 'save_action'):
            self.save_action = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton), "&Save", self)
            self.save_action.setShortcut("Ctrl+S")
            self.save_action.setStatusTip("Save changes to INI file")
            self.save_action.triggered.connect(self.saveFile)
            self.save_action.setEnabled(False)
        file_menu.addAction(self.save_action)
        
        # Add close file action
        close_file_action = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogCloseButton), "&Close File", self)
        close_file_action.setShortcut("Ctrl+W")
        close_file_action.setStatusTip("Close the current file")
        close_file_action.triggered.connect(self.closeFile)
        close_file_action.setEnabled(False)
        self.close_file_action = close_file_action
        file_menu.addAction(close_file_action)
        
        file_menu.addSeparator()
        
        export_action = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton), "Export to &JSON", self)
        export_action.setStatusTip("Export settings to JSON file")
        export_action.triggered.connect(self.exportToJson)
        export_action.setEnabled(False)
        
        import_action = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton), "Import from J&SON", self)
        import_action.setStatusTip("Import settings from JSON file")
        import_action.triggered.connect(self.importFromJson)
        import_action.setEnabled(False)
        
        file_menu.addSeparator()
        
        exit_action = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogCloseButton), "&Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menu_bar.addMenu("&Edit")
        
        reset_action = QAction("&Reset All Settings", self)
        reset_action.setStatusTip("Reset all settings to default values")
        reset_action.triggered.connect(self.resetAllSettings)
        edit_menu.addAction(reset_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("&Help")
        
        about_action = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation), "&About", self)
        about_action.setStatusTip("Show information about the application")
        about_action.triggered.connect(self.showAbout)
        help_menu.addAction(about_action)
    
    def setupToolbar(self):
        """Setup the application toolbar with actions"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Initialize save action first with proper connection
        if not hasattr(self, 'save_action'):
            self.save_action = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton), "Save", self)
            self.save_action.setStatusTip("Save changes to INI file")
            self.save_action.triggered.connect(self.saveFile)  # Ensure direct connection
            self.save_action.setEnabled(False)

        # Create other actions if they don't exist
        if not hasattr(self, 'open_action'):
            self.open_action = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon), "Open", self)
            self.open_action.setStatusTip("Open an INI file")
            self.open_action.triggered.connect(self.openFile)
        
        if not hasattr(self, 'export_action'):
            self.export_action = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView), "Export", self)
            self.export_action.setStatusTip("Export settings to JSON file")
            self.export_action.triggered.connect(self.exportToJson)
            self.export_action.setEnabled(False)

        if not hasattr(self, 'import_action'):
            self.import_action = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogStart), "Import", self)
            self.import_action.setStatusTip("Import settings from JSON file")
            self.import_action.triggered.connect(self.importFromJson)
            self.import_action.setEnabled(False)

        # Add actions to toolbar
        toolbar.addAction(self.open_action)
        toolbar.addAction(self.save_action)  # Use the class-level instance
        toolbar.addSeparator()
        toolbar.addAction(self.export_action)
        toolbar.addAction(self.import_action)
    
    def createSplashScreen(self):
        """Create the initial splash screen when no file is loaded"""
        splash_widget = QWidget()
        splash_layout = QVBoxLayout(splash_widget)
        splash_layout.setContentsMargins(60, 60, 60, 60)
        splash_layout.setSpacing(20)
        
        # Welcome message with improved styling
        welcome_label = QLabel("Game Settings Editor")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(28)
        font.setBold(True)
        welcome_label.setFont(font)
        
        # Subtitle with improved text
        subtitle_label = QLabel("A modern tool for optimizing your gaming experience")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_font = QFont()
        subtitle_font.setPointSize(14)
        subtitle_label.setFont(subtitle_font)
        
        # Create a card-like frame for information
        card_frame = QFrame()
        card_frame.setFrameShape(QFrame.Shape.StyledPanel)
        card_frame.setFrameShadow(QFrame.Shadow.Raised)
        card_frame.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        
        card_layout = QVBoxLayout(card_frame)
        card_layout.setContentsMargins(30, 30, 30, 30)
        
        # Instructions text
        instructions_label = QLabel("Use the File menu to open a game configuration file")
        instructions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions_font = QFont()
        instructions_font.setPointSize(12)
        instructions_label.setFont(instructions_font)
        
        # Keyboard shortcut info
        shortcut_label = QLabel("Press Ctrl+O to open a file")
        shortcut_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        shortcut_font = QFont()
        shortcut_font.setItalic(True)
        shortcut_label.setFont(shortcut_font)
        
        card_layout.addWidget(instructions_label)
        card_layout.addWidget(shortcut_label)
        
        splash_layout.addStretch()
        splash_layout.addWidget(welcome_label)
        splash_layout.addWidget(subtitle_label)
        splash_layout.addWidget(card_frame)
        splash_layout.addStretch()
        
        self.main_layout.addWidget(splash_widget)
        self.splash_widget = splash_widget
    
    def showAbout(self):
        """Show about dialog"""
        QMessageBox.about(
            self, 
            "About Game Settings Editor",
            "<h1>Game Settings Editor</h1>"
            "<p>Version 1.0</p>"
            "<p>A modern and user-friendly editor for game configuration files.</p>"
            "<p>Supports automatic game detection and custom modules.</p>"
        )
    
    def openFile(self):
        """Open an INI file and detect the game module"""
        # Check for unsaved changes
        if self.edited:
            reply = QMessageBox.question(
                self, "Unsaved Changes", 
                "You have unsaved changes. Do you want to save them before opening a new file?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel, 
                QMessageBox.StandardButton.Save
            )
            
            if reply == QMessageBox.StandardButton.Save:
                self.saveFile()
            elif reply == QMessageBox.StandardButton.Cancel:
                return
        
        # Get last directory from settings
        last_dir = self.app_settings.get('General', 'last_directory', fallback='')
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open INI File", last_dir, "INI Files (*.ini);;All Files (*)"
        )
        
        if not file_path:
            return
        
        # Save the directory for next time
        self.app_settings['General']['last_directory'] = os.path.dirname(file_path)
        
        try:
            # Show loading message
            self.status_bar.showMessage(f"Loading file: {os.path.basename(file_path)}...")
            QApplication.processEvents()  # Update the UI
            
            # Detect game from file
            detected_game, module = self.module_loader.detect_game_from_file(file_path)
            
            if module:
                # Load the settings from the file
                self.current_module = module
                self.current_file_path = file_path
                
                # Parse the ini file using the module's parser
                self.settings_data = module.parse_ini_file(file_path)
                
                # Clear main layout and create UI for the module
                self.clearMainLayout()
                self.createModuleUI(detected_game, module)
                
                # Update status and enable save
                self.status_bar.showMessage(f"Loaded {detected_game} settings from {os.path.basename(file_path)}")
                self.save_action.setEnabled(True)
                self.export_action.setEnabled(True)
                self.import_action.setEnabled(True)
                self.close_file_action.setEnabled(True)
                self.edited = False
                
                # Update window title to include file name
                self.setWindowTitle(f"Game Settings Editor - {os.path.basename(file_path)}")
            else:
                # No specific module found, load generic module
                generic_module = GenericModule()
                self.current_module = generic_module
                self.current_file_path = file_path
                
                # Parse the ini file using the generic parser
                self.settings_data = generic_module.parse_ini_file(file_path)
                
                # Clear main layout and create UI for generic editing
                self.clearMainLayout()
                self.createModuleUI("Generic", generic_module)
                
                # Update status and enable save
                self.status_bar.showMessage(f"Loaded generic INI file: {os.path.basename(file_path)}")
                self.save_action.setEnabled(True)
                self.export_action.setEnabled(True)
                self.import_action.setEnabled(True)
                self.close_file_action.setEnabled(True)
                self.edited = False
                
                # Update window title to include file name
                self.setWindowTitle(f"Game Settings Editor - {os.path.basename(file_path)} (Generic)")
        
        except Exception as e:
            error_message = f"Failed to open file: {str(e)}"
            QMessageBox.critical(self, "Error Opening File", error_message)
            self.status_bar.showMessage(f"Error: {error_message}")
    
    def clearMainLayout(self):
        """Clear the main layout to prepare for loading a new module UI"""
        # Remove the splash screen or previous module UI
        if hasattr(self, 'splash_widget') and self.splash_widget:
            self.splash_widget.setParent(None)
            self.splash_widget = None
        
        if hasattr(self, 'module_widget') and self.module_widget:
            self.module_widget.setParent(None)
            self.module_widget = None
        
        # Clear any other widgets in the main layout
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
    
    def createModuleUI(self, game_name, module):
        """Create the UI for a specific module"""
        # Create main widget and layout
        module_widget = QWidget()
        module_layout = QVBoxLayout(module_widget)
        module_layout.setContentsMargins(10, 10, 10, 10)
        module_layout.setSpacing(10)
        
        # Store reference to module widget and layout
        self.module_widget = module_widget
        self.module_layout = module_layout
        
        
        # Only show header for non-Palworld games
        if game_name.lower() != "palworld":
            # Create header with game name and icon
            header_widget = QWidget()
            header_widget.setObjectName("headerWidget")
            header_widget.setStyleSheet("""
                #headerWidget {
                    background-color: #3498db;
                    border-radius: 5px;
                    margin-bottom: 10px;
                }
            """)
            
            header_layout = QHBoxLayout(header_widget)
            header_layout.setContentsMargins(20, 15, 20, 15)
            
            # Add game icon
            game_icon = QLabel()
            icon = self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
            game_icon.setPixmap(icon.pixmap(48, 48))
            header_layout.addWidget(game_icon)
            
            # Add game name in large text
            header_label = QLabel(f"{game_name} Settings Editor")
            header_label.setStyleSheet("color: white; font-weight: bold;")
            header_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            font = QFont()
            font.setPointSize(16)
            font.setBold(True)
            header_label.setFont(font)
            header_layout.addWidget(header_label, 1)
            
            module_layout.addWidget(header_widget)
            
            # Create info label
            info_label = QLabel(f"Editing configuration file: {os.path.basename(self.current_file_path)}")
            info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            info_font = QFont()
            info_font.setItalic(True)
            info_label.setFont(info_font)
            module_layout.addWidget(info_label)
        else:
            # For Palworld, show file info in the status bar instead of a label
            self.statusBar().showMessage(f"Editing: {os.path.basename(self.current_file_path)}")
        
        # Create search widget if we have a lot of settings
        if len(module.get_all_settings()) > 10:
            search_widget = QWidget()
            search_layout = QHBoxLayout(search_widget)
            search_layout.setContentsMargins(0, 0, 0, 10)
            
            search_label = QLabel("Search:")
            search_layout.addWidget(search_label)
            
            search_input = QLineEdit()
            search_input.setPlaceholderText("Type to search settings...")
            search_input.textChanged.connect(self.filterSettings)
            self.search_input = search_input
            search_layout.addWidget(search_input, 1)
            
            module_layout.addWidget(search_widget)
        
        # Create a container for the main content (will be hidden during search)
        self.main_content_widget = QWidget()
        main_content_layout = QVBoxLayout(self.main_content_widget)
        main_content_layout.setContentsMargins(0, 0, 0, 0)
        main_content_layout.setSpacing(10)
        module_layout.addWidget(self.main_content_widget)
        
        # Palworld special left panel for tabs, right side for settings
        if game_name.lower() == "palworld":
            # Create a splitter for left/right panels
            splitter = QSplitter(Qt.Orientation.Horizontal)
            
            # Left panel for category selection - more compact
            left_panel = QWidget()
            left_layout = QVBoxLayout(left_panel)
            left_layout.setContentsMargins(3, 3, 3, 3)
            left_layout.setSpacing(5)
            
            # Add a header for the categories
            category_header = QLabel("Categories")
            category_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
            header_font = QFont()
            header_font.setPointSize(11)
            header_font.setBold(True)
            category_header.setFont(header_font)
            left_layout.addWidget(category_header)
            
            # Create a list widget for categories - narrower
            category_list = QListWidget()
            category_list.setMinimumWidth(150)
            category_list.setMaximumWidth(180)
            category_list.setStyleSheet("""
                QListWidget {
                    background-color: #2d2d2d;
                    border-radius: 5px;
                    padding: 3px;
                }
                QListWidget::item {
                    padding: 6px;
                    border-radius: 3px;
                }
                QListWidget::item:selected {
                    background-color: #1e2a38;
                    color: white;
                }
                QListWidget::item:hover:!selected {
                    background-color: #3a3a3a;
                }
            """)
            
            # Get categories
            if hasattr(module, 'get_categories') and callable(module.get_categories):
                categories = module.get_categories()
                
                # Add categories to list with icons
                for category in categories:
                    item = QListWidgetItem(category)
                    item.setIcon(self.getCategoryIcon(category))
                    category_list.addItem(item)
                
                # Connect selection change
                category_list.currentRowChanged.connect(lambda idx: self.showCategorySettings(idx, categories, module, right_panel))
                
                left_layout.addWidget(category_list)
                
                # Right panel for settings
                right_panel = QWidget()
                right_layout = QVBoxLayout(right_panel)
                right_layout.setContentsMargins(10, 10, 10, 10)
                
                # Add panels to splitter
                splitter.addWidget(left_panel)
                splitter.addWidget(right_panel)
                
                # Set initial sizes (20% left, 80% right) - make right side wider
                splitter.setSizes([200, 800])
                
                # Add splitter to main layout
                main_content_layout.addWidget(splitter, 1)
                
                # Select first category by default
                if categories:
                    category_list.setCurrentRow(0)
            else:
                # Fallback to standard layout if no categories
                self.createSettingsForm(main_content_layout, module)
        else:
            # Standard tabbed interface for other games
            if hasattr(module, 'get_categories') and callable(module.get_categories):
                categories = module.get_categories()
                if categories:
                    tab_widget = QTabWidget()
                    tab_widget.setDocumentMode(True)
                    tab_widget.setTabPosition(QTabWidget.TabPosition.North)
                    
                    # Create a tab for each category
                    for category in categories:
                        category_widget = QWidget()
                        category_layout = QGridLayout(category_widget)
                        category_layout.setContentsMargins(15, 15, 15, 15)
                        category_layout.setHorizontalSpacing(15)
                        category_layout.setVerticalSpacing(10)
                        category_layout.setColumnStretch(0, 0)  # Label column
                        category_layout.setColumnStretch(1, 1)  # Widget column
                        category_layout.setColumnStretch(2, 0)  # Reset column
                        
                        # Get settings for this category
                        category_settings = module.get_settings_by_category(category)
                        
                        # Create UI elements for each setting
                        row = 0
                        for setting in category_settings:
                            widgets = self.addSettingToLayout(category_layout, setting, module, row)
                            # Tag widgets with category for filtering
                            for widget in widgets:
                                if widget:
                                    widget.setProperty("category", category)
                                    widget.setProperty("setting_name", setting.get('name', ''))
                            row += 1
                        
                        # Add a scroll area for the category
                        scroll = QScrollArea()
                        scroll.setWidgetResizable(True)
                        scroll.setWidget(category_widget)
                        
                        # Add tab with icon based on category
                        icon = self.getCategoryIcon(category)
                        tab_widget.addTab(scroll, icon, category)
                    
                    main_content_layout.addWidget(tab_widget, 1)
                else:
                    # No categories, create a single form
                    self.createSettingsForm(main_content_layout, module)
            else:
                # Module doesn't support categories, create a single form
                self.createSettingsForm(main_content_layout, module)
        
        # Add bottom buttons (reset, etc.)
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(0, 10, 0, 0)
        
        # Add info about edited status
        self.edit_status_label = QLabel("No changes made")
        button_layout.addWidget(self.edit_status_label)
        
        button_layout.addStretch()
        
        # Reset button with icon
        reset_all_button = QPushButton("Reset All")
        reset_all_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
        reset_all_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        reset_all_button.clicked.connect(self.resetAllSettings)
        button_layout.addWidget(reset_all_button)
        
        main_content_layout.addWidget(button_widget)
        
        # Add the module widget to the main layout
        self.main_layout.addWidget(module_widget)
        
        # Force update of the UI
        self.central_widget.update()
        QApplication.processEvents()
        
        print(f"Module UI created and added to main layout")
    
    def getCategoryIcon(self, category):
        """Get an appropriate icon for a settings category"""
        category_lower = category.lower()
        
        if "general" in category_lower:
            return self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogInfoView)
        elif "server" in category_lower or "multiplayer" in category_lower:
            return self.style().standardIcon(QStyle.StandardPixmap.SP_DriveNetIcon)
        elif "graphics" in category_lower or "display" in category_lower:
            return self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        elif "audio" in category_lower or "sound" in category_lower:
            return self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume)
        elif "input" in category_lower or "controls" in category_lower:
            return self.style().standardIcon(QStyle.StandardPixmap.SP_DialogHelpButton)
        elif "advanced" in category_lower:
            return self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView)
        elif "gameplay" in category_lower:
            return self.style().standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton)
        elif "damage" in category_lower or "health" in category_lower:
            return self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning)
        elif "building" in category_lower or "basebuilding" in category_lower:
            return self.style().standardIcon(QStyle.StandardPixmap.SP_DirHomeIcon)
        
        # Default icon
        return self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
    
    def filterSettings(self, text):
        """Filter settings based on search text"""
        try:
            # If we have a search results panel already, remove it
            if hasattr(self, 'search_results_panel') and self.search_results_panel:
                self.search_results_panel.setParent(None)
                self.search_results_panel = None
            
            # If search is empty, restore normal view
            if not text or not text.strip():
                # Show all normal UI elements
                if hasattr(self, 'main_content_widget'):
                    self.main_content_widget.setVisible(True)
                return
            
            # Hide the main content when searching
            if hasattr(self, 'main_content_widget'):
                self.main_content_widget.setVisible(False)
            
            # Create a search results panel
            self.search_results_panel = QWidget()
            self.search_results_panel.setObjectName("searchResultsPanel")
            
            # Add the search results panel to the main layout
            if hasattr(self, 'main_layout') and self.main_layout:
                self.main_layout.addWidget(self.search_results_panel)
            else:
                # Fallback if main_layout is not available
                self.centralWidget().layout().addWidget(self.search_results_panel)
            
            # Create layout for search results
            results_layout = QVBoxLayout(self.search_results_panel)
            results_layout.setContentsMargins(10, 10, 10, 10)
            results_layout.setSpacing(10)
            
            # Add a header for search results
            header = QLabel(f"Search Results for: '{text}'")
            header.setStyleSheet("font-weight: bold; font-size: 14px; color: #3498db;")
            results_layout.addWidget(header)
            
            # Create a scroll area for results
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            
            # Container for results
            results_container = QWidget()
            results_container_layout = QVBoxLayout(results_container)
            results_container_layout.setContentsMargins(5, 5, 5, 5)
            results_container_layout.setSpacing(10)
            
            # Get all settings from the current module
            if self.current_module and hasattr(self.current_module, 'get_all_settings'):
                all_settings = self.current_module.get_all_settings()
                
                # Filter settings based on search text
                text = text.lower()
                matching_settings = []
                
                for setting in all_settings:
                    name = setting.get('name', '').lower()
                    description = setting.get('description', '').lower()
                    category = setting.get('category', '').lower()
                    
                    # Check if setting matches search
                    if (text in name or text in description or text in category):
                        matching_settings.append(setting)
                
                # If no results found
                if not matching_settings:
                    no_results = QLabel("No matching settings found.")
                    no_results.setStyleSheet("color: #aaa; font-style: italic;")  # Lighter color for dark mode
                    results_container_layout.addWidget(no_results)
                    results_container_layout.addStretch(1)
                else:
                    # Group results by category
                    categories = {}
                    for setting in matching_settings:
                        category = setting.get('category', 'Uncategorized')
                        if category not in categories:
                            categories[category] = []
                        categories[category].append(setting)
                    
                    # Add results by category
                    for category, settings in categories.items():
                        # Add category header
                        category_widget = QWidget()
                        category_layout = QVBoxLayout(category_widget)
                        category_layout.setContentsMargins(0, 0, 0, 0)
                        category_layout.setSpacing(5)
                        
                        category_header = QLabel(category)
                        category_header.setStyleSheet("font-weight: bold; background-color: #1e2a38; color: white; padding: 5px; border-radius: 3px;")
                        category_layout.addWidget(category_header)
                        
                        # Add settings in this category
                        for setting in settings:
                            # Create a widget for this setting
                            setting_widget = QWidget()
                            setting_widget.setStyleSheet("background-color: #2d2d2d; border-radius: 3px; padding: 5px;")  # Dark background for dark mode
                            setting_layout = QGridLayout(setting_widget)
                            setting_layout.setContentsMargins(10, 10, 10, 10)
                            setting_layout.setHorizontalSpacing(15)
                            setting_layout.setVerticalSpacing(5)
                            
                            # Setting name
                            name_label = QLabel(setting.get('name', ''))
                            name_label.setStyleSheet("font-weight: bold; color: #ddd;")  # Light text for dark mode
                            setting_layout.addWidget(name_label, 0, 0)
                            
                            # Get the widget for this setting
                            widget = None
                            if setting.get('name') in self.ui_elements:
                                # Create a clone of the widget
                                original_widget = self.ui_elements[setting.get('name')]
                                widget = self.cloneWidgetForSearch(original_widget, setting)
                                setting_layout.addWidget(widget, 0, 1)
                            
                            # Description (if available)
                            if setting.get('description'):
                                desc_label = QLabel(setting.get('description'))
                                desc_label.setWordWrap(True)
                                desc_label.setStyleSheet("color: #aaa; font-style: italic; font-size: 8pt;")  # Lighter color for dark mode
                                setting_layout.addWidget(desc_label, 1, 0, 1, 2)
                            
                            category_layout.addWidget(setting_widget)
                        
                        results_container_layout.addWidget(category_widget)
                    
                    # Add stretch at the end
                    results_container_layout.addStretch(1)
            
            scroll.setWidget(results_container)
            results_layout.addWidget(scroll)
            
        except Exception as e:
            QMessageBox.critical(self, "Search Error", f"An error occurred during search: {str(e)}")
    
    def cloneWidgetForSearch(self, original_widget, setting):
        """Create a clone of a widget for the search results panel"""
        name = setting.get('name', '')
        setting_type = setting.get('type', 'string')
        
        # Get current value
        current_value = self.settings_data.get(name, setting.get('default', ''))
        
        # Create appropriate widget based on setting type
        if setting_type == 'integer':
            widget = QSpinBox()
            widget.setMinimumWidth(150)
            min_val = setting.get('min', -2147483647)
            max_val = setting.get('max', 2147483647)
            widget.setRange(min_val, max_val)
            widget.setGroupSeparatorShown(True)
            
            if current_value:
                try:
                    widget.setValue(int(current_value))
                except (ValueError, TypeError):
                    widget.setValue(0)
            widget.valueChanged.connect(lambda val, s=name: self.onSettingChanged(s, val))
            
            # Apply dark mode styling
            widget.setStyleSheet("background-color: #333; color: #ddd; border: 1px solid #555;")
            
        elif setting_type == 'float':
            widget = QDoubleSpinBox()
            widget.setMinimumWidth(150)
            min_val = setting.get('min', -1000000.0)
            max_val = setting.get('max', 1000000.0)
            widget.setRange(min_val, max_val)
            widget.setDecimals(6)
            widget.setGroupSeparatorShown(True)
            
            if current_value:
                try:
                    widget.setValue(float(current_value))
                except (ValueError, TypeError):
                    widget.setValue(0.0)
            widget.valueChanged.connect(lambda val, s=name: self.onSettingChanged(s, val))
            
            # Apply dark mode styling
            widget.setStyleSheet("background-color: #333; color: #ddd; border: 1px solid #555;")
            
        elif setting_type == 'boolean':
            widget = QCheckBox("Enabled")
            if isinstance(current_value, str):
                widget.setChecked(current_value.lower() in ('true', 'yes', '1'))
            else:
                widget.setChecked(bool(current_value))
            widget.stateChanged.connect(lambda state, s=name: self.onSettingChanged(s, state == Qt.CheckState.Checked))
            
            # Apply dark mode styling
            widget.setStyleSheet("color: #ddd;")
            
        elif setting_type == 'enum':
            widget = QComboBox()
            widget.setMinimumWidth(150)
            options = setting.get('options', [])
            for option in options:
                widget.addItem(option)
            
            if current_value and current_value in options:
                widget.setCurrentText(current_value)
            widget.currentTextChanged.connect(lambda text, s=name: self.onSettingChanged(s, text))
            
            # Apply dark mode styling
            widget.setStyleSheet("background-color: #333; color: #ddd; border: 1px solid #555;")
            
        else:  # Default to string
            widget = QLineEdit()
            widget.setMinimumWidth(150)
            if current_value:
                widget.setText(str(current_value))
            widget.textChanged.connect(lambda text, s=name: self.onSettingChanged(s, text))
            
            # Apply dark mode styling
            widget.setStyleSheet("background-color: #333; color: #ddd; border: 1px solid #555;")
        
        return widget
    
    def createSettingsForm(self, parent_layout, module):
        """Create a form layout for all settings when there are no categories"""
        form_widget = QWidget()
        form_layout = QGridLayout(form_widget)
        form_layout.setContentsMargins(15, 15, 15, 15)
        form_layout.setHorizontalSpacing(15)
        form_layout.setVerticalSpacing(10)
        form_layout.setColumnStretch(0, 0)  # Label column
        form_layout.setColumnStretch(1, 1)  # Widget column
        form_layout.setColumnStretch(2, 0)  # Reset column
        
        # Get all settings
        settings = module.get_all_settings()
        
        # Create UI elements for each setting
        row = 0
        for setting in settings:
            self.addSettingToLayout(form_layout, setting, module, row)
            row += 1
        
        # Add a scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(form_widget)
        
        parent_layout.addWidget(scroll, 1)
    
    def addSettingToLayout(self, layout, setting, module, row):
        """Add a setting to the given layout with the appropriate widget type"""
        name = setting.get('name', '')
        setting_type = setting.get('type', 'string')
        description = setting.get('description', '')
        
        # Check if this is Palworld module - use more compact UI
        is_palworld = self.current_module and hasattr(self.current_module, 'get_game_name') and self.current_module.get_game_name().lower() == 'palworld'
        
        # Create label with tooltip for description
        label = QLabel(name)
        label.setToolTip(description)
        font = QFont()
        font.setBold(True)
        if is_palworld:
            font.setPointSize(9)  # Smaller font for Palworld
        label.setFont(font)
        
        # Create a container for the setting widget and its description
        container = QWidget()
        container_layout = QVBoxLayout(container)
        
        # Make layout more compact for Palworld
        if is_palworld:
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setSpacing(3)  # Slightly increased spacing
        else:
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setSpacing(4)  # Slightly increased spacing
        
        # Get current value from settings data - ensure we're getting the value correctly
        current_value = None
        if name in self.settings_data:
            current_value = self.settings_data[name]
        else:
            current_value = setting.get('default', '')
            # Store the default value in settings_data if not present
            self.settings_data[name] = current_value
    

        
        # Create appropriate widget based on setting type
        if setting_type == 'integer':
            widget = QSpinBox()
            if is_palworld:
                widget.setMinimumWidth(120)
            else:
                widget.setMinimumWidth(150)
            min_val = setting.get('min', -2147483647)
            max_val = setting.get('max', 2147483647)
            widget.setRange(min_val, max_val)
            
            # Add thousands separator for better readability
            widget.setGroupSeparatorShown(True)
            
            if current_value:
                try:
                    widget.setValue(int(current_value))
                except (ValueError, TypeError):
                    widget.setValue(0)
            widget.valueChanged.connect(lambda val, s=name: self.onSettingChanged(s, val))
        
        elif setting_type == 'float':
            widget = QDoubleSpinBox()
            if is_palworld:
                widget.setMinimumWidth(120)
            else:
                widget.setMinimumWidth(150)
            min_val = setting.get('min', -1000000.0)
            max_val = setting.get('max', 1000000.0)
            widget.setRange(min_val, max_val)
            widget.setDecimals(6)
            
            # Add thousands separator for better readability
            widget.setGroupSeparatorShown(True)
            
            if current_value:
                try:
                    widget.setValue(float(current_value))
                except (ValueError, TypeError):
                    widget.setValue(0.0)
            widget.valueChanged.connect(lambda val, s=name: self.onSettingChanged(s, val))
        
        elif setting_type == 'boolean':
            widget = QCheckBox("Enabled")
            if isinstance(current_value, str):
                widget.setChecked(current_value.lower() in ('true', 'yes', '1'))
            else:
                widget.setChecked(bool(current_value))
            widget.stateChanged.connect(lambda state, s=name: self.onSettingChanged(s, state == Qt.CheckState.Checked))
        
        elif setting_type == 'enum':
            widget = QComboBox()
            if is_palworld:
                widget.setMinimumWidth(120)
            else:
                widget.setMinimumWidth(150)
            options = setting.get('options', [])
            for option in options:
                widget.addItem(option)
            
            if current_value and current_value in options:
                widget.setCurrentText(current_value)
            widget.currentTextChanged.connect(lambda text, s=name: self.onSettingChanged(s, text))
        
        else:  # Default to string
            widget = QLineEdit()
            if is_palworld:
                widget.setMinimumWidth(120)
            else:
                widget.setMinimumWidth(150)
            if current_value:
                widget.setText(str(current_value))
            widget.textChanged.connect(lambda text, s=name: self.onSettingChanged(s, text))
        
        # Add the widget to the container
        container_layout.addWidget(widget)
        
        # Always add description if available (even for Palworld)
        if description:
            desc_label = QLabel(description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #aaa; font-size: 8pt; margin-top: 2px;")  # Lighter color for dark mode
            container_layout.addWidget(desc_label)
        
        # Create reset button with icon instead of text
        reset_button = QToolButton()
        reset_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
        reset_button.setToolTip(f"Reset to default: {setting.get('default', '')}")
        reset_button.setFixedSize(24, 24)  # Make it square and compact
        reset_button.clicked.connect(lambda checked, s=setting: self.resetSetting(s))
        
        # Add widgets to layout with proper alignment
        layout.addWidget(label, row, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        layout.addWidget(container, row, 1)
        layout.addWidget(reset_button, row, 2, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        # Store widget reference for later access
        self.ui_elements[name] = widget
        
        # Return the created widgets for potential further customization
        return [label, container, reset_button]
    
    def onSettingChanged(self, setting_name, value):
        """Handle when a setting is changed by the user"""
        self.settings_data[setting_name] = value
        self.edited = True
        
        # Update status
        if self.current_file_path:
            file_name = os.path.basename(self.current_file_path)
            self.status_bar.showMessage(f"Editing {file_name} - Unsaved changes")
            
            # Update edit status label if available
            if hasattr(self, 'edit_status_label'):
                self.edit_status_label.setText("Changes not saved")
                self.edit_status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
    
    def resetSetting(self, setting):
        """Reset a single setting to its default value"""
        name = setting.get('name', '')
        default = setting.get('default', '')
        
        if name in self.ui_elements:
            widget = self.ui_elements[name]
            setting_type = setting.get('type', 'string')
            
            # Set the widget value based on type
            if setting_type == 'integer':
                try:
                    widget.setValue(int(default))
                except (ValueError, TypeError):
                    widget.setValue(0)
            elif setting_type == 'float':
                try:
                    widget.setValue(float(default))
                except (ValueError, TypeError):
                    widget.setValue(0.0)
            elif setting_type == 'boolean':
                widget.setChecked(default.lower() in ('true', 'yes', '1'))
            elif setting_type == 'enum':
                widget.setCurrentText(default)
            else:  # string
                widget.setText(default)
            
            # Update the settings data
            self.settings_data[name] = default
            self.edited = True
            
            # Update status
            if self.current_file_path:
                file_name = os.path.basename(self.current_file_path)
                self.status_bar.showMessage(f"Reset {name} to default value")
    
    def resetAllSettings(self):
        """Reset all settings to their default values"""
        if not self.current_module:
            return
        
        # Confirm reset
        reply = QMessageBox.question(
            self, "Reset All Settings", 
            "Are you sure you want to reset all settings to their default values?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Get default values from module
            defaults = {}
            for setting in self.current_module.get_all_settings():
                name = setting.get('name', '')
                default = setting.get('default', '')
                defaults[name] = default
                
                # Update UI element
                if name in self.ui_elements:
                    self.resetSetting(setting)
            
            # Update settings data with defaults
            self.settings_data = defaults
            self.edited = True
            
            # Update status
            if self.current_file_path:
                file_name = os.path.basename(self.current_file_path)
                self.status_bar.showMessage(f"Reset all settings to default values")
                
                # Update edit status label if available
                if hasattr(self, 'edit_status_label'):
                    self.edit_status_label.setText("All settings reset to defaults (not saved)")
                    self.edit_status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
    
    def saveFile(self):
        """Save settings to the INI file"""
        if not self.current_module or not self.current_file_path:
            return
        
        try:
            # Show a temporary "Saving..." message
            self.status_bar.showMessage("Saving changes...")
            QApplication.processEvents()  # Update the UI
            
            # Save the settings using the module's save method
            self.current_module.save_ini_file(self.current_file_path, self.settings_data)
            
            # Update status
            self.edited = False
            file_name = os.path.basename(self.current_file_path)
            self.status_bar.showMessage(f"Changes saved to {file_name}", 5000)
            
            # Update edit status label if available
            if hasattr(self, 'edit_status_label'):
                self.edit_status_label.setText("All changes saved")
                self.edit_status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
            
        except Exception as e:
            QMessageBox.critical(self, "Error Saving File", f"Failed to save file: {str(e)}")
    
    def exportToJson(self):
        """Export current settings to a JSON file"""
        if not self.current_module or not self.current_file_path:
            return
        
        # Get the directory and filename from the current INI file
        ini_dir = os.path.dirname(self.current_file_path)
        ini_basename = os.path.splitext(os.path.basename(self.current_file_path))[0]
        
        # Suggest a JSON filename
        suggested_path = os.path.join(ini_dir, f"{ini_basename}_export.json")
        
        # Show save dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Settings to JSON", suggested_path, "JSON Files (*.json)"
        )
        
        if not file_path:
            return
        
        try:
            # Show a temporary "Exporting..." message
            self.status_bar.showMessage("Exporting to JSON...")
            QApplication.processEvents()  # Update the UI
            
            # Create a dictionary with metadata
            export_data = {
                "game": self.current_module.get_game_name(),
                "source_file": self.current_file_path,
                "export_date": datetime.datetime.now().isoformat(),
                "settings": self.settings_data
            }
            
            # Write to JSON file with indentation
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2)
            
            # Update status
            self.status_bar.showMessage(f"Settings exported to {os.path.basename(file_path)}", 5000)
            
        except Exception as e:
            QMessageBox.critical(self, "Error Exporting", f"Failed to export settings: {str(e)}")
    
    def importFromJson(self):
        """Import settings from a JSON file"""
        if not self.current_module or not self.current_file_path:
            return
        
        # Get the directory from the current INI file
        ini_dir = os.path.dirname(self.current_file_path)
        
        # Show open dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Settings from JSON", ini_dir, "JSON Files (*.json)"
        )
        
        if not file_path:
            return
        
        try:
            # Read JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Check if this is a valid export file
            if not isinstance(import_data, dict) or "settings" not in import_data:
                QMessageBox.warning(self, "Invalid Import", "The selected file is not a valid settings export.")
                return
            
            # Show confirmation, especially if the game doesn't match
            current_game = self.current_module.get_game_name()
            imported_game = import_data.get("game", "Unknown")
            
            if imported_game != current_game:
                reply = QMessageBox.question(
                    self, "Game Mismatch", 
                    f"The imported settings are for '{imported_game}', but you are editing '{current_game}'.\n\n"
                    f"Do you still want to import these settings?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                    QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.No:
                    return
            
            # Import the settings
            imported_settings = import_data["settings"]
            
            # Show a temporary "Importing..." message
            self.status_bar.showMessage("Importing settings...")
            QApplication.processEvents()  # Update the UI
            
            # Apply imported settings to UI
            for name, value in imported_settings.items():
                if name in self.ui_elements:
                    widget = self.ui_elements[name]
                    
                    # Update widget based on its type
                    if isinstance(widget, QSpinBox):
                        try:
                            widget.setValue(int(value))
                        except (ValueError, TypeError):
                            pass
                    elif isinstance(widget, QDoubleSpinBox):
                        try:
                            widget.setValue(float(value))
                        except (ValueError, TypeError):
                            pass
                    elif isinstance(widget, QCheckBox):
                        if isinstance(value, str):
                            widget.setChecked(value.lower() in ('true', 'yes', '1'))
                        else:
                            widget.setChecked(bool(value))
                    elif isinstance(widget, QComboBox):
                        try:
                            widget.setCurrentText(str(value))
                        except:
                            pass
                    elif isinstance(widget, QLineEdit):
                        widget.setText(str(value))
            
            # Update settings data
            self.settings_data.update(imported_settings)
            self.edited = True
            
            # Update status
            self.status_bar.showMessage(f"Settings imported from {os.path.basename(file_path)} - Unsaved changes", 5000)
            
            # Update edit status label if available
            if hasattr(self, 'edit_status_label'):
                self.edit_status_label.setText("Imported settings (not saved)")
                self.edit_status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
            
        except Exception as e:
            QMessageBox.critical(self, "Error Importing", f"Failed to import settings: {str(e)}")
    
    def validateSettings(self):
        """Validate all settings according to their constraints using regex patterns"""
        if not self.current_module or not self.settings_data:
            return True
        
        errors = []
        
        for setting in self.current_module.get_all_settings():
            name = setting.get('name', '')
            setting_type = setting.get('type', 'string')
            
            # Skip if setting not in current data
            if name not in self.settings_data:
                continue
                
            value = self.settings_data[name]
            
            # Validate based on type
            if setting_type == 'string' and 'pattern' in setting:
                pattern = setting['pattern']
                if not re.match(pattern, str(value)):
                    errors.append(f"'{name}' does not match the required pattern")
            
            elif setting_type == 'integer':
                min_val = setting.get('min', -2147483647)
                max_val = setting.get('max', 2147483647)
                try:
                    int_val = int(value)
                    if int_val < min_val or int_val > max_val:
                        errors.append(f"'{name}' must be between {min_val} and {max_val}")
                except ValueError:
                    errors.append(f"'{name}' must be an integer")
            
            elif setting_type == 'float':
                min_val = setting.get('min', -1000000.0)
                max_val = setting.get('max', 1000000.0)
                try:
                    float_val = float(value)
                    if float_val < min_val or float_val > max_val:
                        errors.append(f"'{name}' must be between {min_val} and {max_val}")
                except ValueError:
                    errors.append(f"'{name}' must be a number")
        
        if errors:
            error_msg = "The following validation errors were found:\n\n" + "\n".join(errors)
            QMessageBox.warning(self, "Validation Errors", error_msg)
            return False
            
        return True
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Check for unsaved changes
        if self.edited:
            reply = QMessageBox.question(
                self, "Unsaved Changes", 
                "You have unsaved changes. Do you want to save them before exiting?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel, 
                QMessageBox.StandardButton.Save
            )
            
            if reply == QMessageBox.StandardButton.Save:
                self.saveFile()
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
        
        # Save application settings
        self.save_app_settings()
        
        # Accept the event (close the window)
        event.accept()

    def showCategorySettings(self, index, categories, module, right_panel):
        """Show settings for a selected category"""
        if index < 0 or index >= len(categories):
            return
            
        # Clear the right panel
        for i in reversed(range(right_panel.layout().count())): 
            right_panel.layout().itemAt(i).widget().setParent(None)
        
        category = categories[index]
        
        # Get settings for this category
        settings = module.get_settings_by_category(category)
        
        
        # Create a form layout for the settings
        form_widget = QWidget()
        form_layout = QGridLayout(form_widget)
        form_layout.setContentsMargins(10, 10, 10, 10)
        form_layout.setHorizontalSpacing(15)
        form_layout.setVerticalSpacing(10)
        form_layout.setColumnStretch(0, 0)  # Label column
        form_layout.setColumnStretch(1, 1)  # Widget column
        form_layout.setColumnStretch(2, 0)  # Reset column
        
        # Add settings to the form
        row = 0
        for setting in settings:
            self.addSettingToLayout(form_layout, setting, module, row)
            row += 1
        
        # Add a scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(form_widget)
        
        # Add to right panel
        right_panel.layout().addWidget(scroll)

    def closeFile(self):
        """Close the currently open file and return to the splash screen"""
        # Check for unsaved changes
        if self.edited:
            reply = QMessageBox.question(
                self, 
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before closing?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                self.saveFile()
            elif reply == QMessageBox.StandardButton.Cancel:
                return
        
        # Clear the main layout
        self.clearMainLayout()
        
        # Reset variables
        self.current_module = None
        self.current_file_path = None
        self.settings_data = {}
        self.ui_elements = {}
        self.edited = False
        
        # Disable actions
        self.save_action.setEnabled(False)
        self.close_file_action.setEnabled(False)
        self.export_action.setEnabled(False)
        self.import_action.setEnabled(False)
        
        # Clear status bar
        self.statusBar().clearMessage()
        
        # Show splash screen
        self.createSplashScreen()


def main():
    app = QApplication(sys.argv)
    window = IniEditorApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 