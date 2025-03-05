import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QFormLayout, QLabel,
    QDoubleSpinBox, QSpinBox, QCheckBox, QLineEdit, QComboBox, QFileDialog,
    QMessageBox, QVBoxLayout, QHBoxLayout, QPushButton, QGroupBox, 
    QSplitter, QScrollArea, QSizePolicy, QGridLayout, QFrame, QToolBar,
    QStatusBar, QMenu, QToolButton, QLineEdit, QCompleter, QTextEdit
)
from PyQt6.QtGui import (
    QAction, QIcon, QFont, QPalette, QColor, QPixmap, QCursor, 
    QGuiApplication, QScreen, QFontMetrics
)
from PyQt6.QtCore import Qt, QSize, QTimer, QStringListModel
import re
import os

# Define all settings with categories, types, and descriptions as comments
settings_definitions = [
    # General Settings
    {"name": "Difficulty", "category": "General", "type": "enum", "options": ["None", "Casual", "Normal", "Hard"], "description": "Sets the game difficulty level. 'None' uses custom settings."},
    {"name": "DayTimeSpeedRate", "category": "General", "type": "float", "min": 0.1, "max": 10.0, "description": "Adjusts how fast daytime progresses in the game."},
    {"name": "NightTimeSpeedRate", "category": "General", "type": "float", "min": 0.1, "max": 10.0, "description": "Adjusts how fast nighttime progresses in the game."},
    {"name": "ExpRate", "category": "General", "type": "float", "min": 0.1, "max": 100.0, "description": "Multiplies the rate at which players gain experience points."},
    {"name": "PalCaptureRate", "category": "General", "type": "float", "min": 0.1, "max": 10.0, "description": "Multiplies the success rate of capturing Pals."},
    {"name": "PalSpawnNumRate", "category": "General", "type": "float", "min": 0.1, "max": 10.0, "description": "Multiplies the number of Pals that spawn in the world."},

    # Damage and Health Settings
    {"name": "PalDamageRateAttack", "category": "Damage and Health", "type": "float", "min": 0.1, "max": 10.0, "description": "Multiplies the attack damage dealt by Pals."},
    {"name": "PalDamageRateDefense", "category": "Damage and Health", "type": "float", "min": 0.1, "max": 10.0, "description": "Multiplies the damage Pals take (defense modifier)."},
    {"name": "PlayerDamageRateAttack", "category": "Damage and Health", "type": "float", "min": 0.1, "max": 10.0, "description": "Multiplies the attack damage dealt by players."},
    {"name": "PlayerDamageRateDefense", "category": "Damage and Health", "type": "float", "min": 0.1, "max": 10.0, "description": "Multiplies the damage players take (defense modifier)."},
    {"name": "PlayerStomachDecreaceRate", "category": "Damage and Health", "type": "float", "min": 0.1, "max": 10.0, "description": "Multiplies how quickly players get hungry."},
    {"name": "PlayerStaminaDecreaceRate", "category": "Damage and Health", "type": "float", "min": 0.1, "max": 10.0, "description": "Multiplies how quickly players lose stamina."},
    {"name": "PlayerAutoHPRegeneRate", "category": "Damage and Health", "type": "float", "min": 0.1, "max": 10.0, "description": "Multiplies the rate of automatic HP regeneration for players."},
    {"name": "PlayerAutoHpRegeneRateInSleep", "category": "Damage and Health", "type": "float", "min": 0.1, "max": 10.0, "description": "Multiplies HP regeneration rate for players while sleeping."},
    {"name": "PalStomachDecreaceRate", "category": "Damage and Health", "type": "float", "min": 0.1, "max": 10.0, "description": "Multiplies how quickly Pals get hungry."},
    {"name": "PalStaminaDecreaceRate", "category": "Damage and Health", "type": "float", "min": 0.1, "max": 10.0, "description": "Multiplies how quickly Pals lose stamina."},
    {"name": "PalAutoHPRegeneRate", "category": "Damage and Health", "type": "float", "min": 0.1, "max": 10.0, "description": "Multiplies the rate of automatic HP regeneration for Pals."},
    {"name": "PalAutoHpRegeneRateInSleep", "category": "Damage and Health", "type": "float", "min": 0.1, "max": 10.0, "description": "Multiplies HP regeneration rate for Pals while sleeping."},

    # Building and Collection Settings
    {"name": "BuildObjectDamageRate", "category": "Building and Collection", "type": "float", "min": 0.1, "max": 10.0, "description": "Multiplies damage dealt to built objects."},
    {"name": "BuildObjectDeteriorationDamageRate", "category": "Building and Collection", "type": "float", "min": 0.1, "max": 10.0, "description": "Multiplies natural deterioration damage to built objects."},
    {"name": "CollectionDropRate", "category": "Building and Collection", "type": "float", "min": 0.1, "max": 10.0, "description": "Multiplies the drop rate of items from collection objects."},
    {"name": "CollectionObjectHpRate", "category": "Building and Collection", "type": "float", "min": 0.1, "max": 10.0, "description": "Multiplies the health of objects that can be collected."},
    {"name": "CollectionObjectRespawnSpeedRate", "category": "Building and Collection", "type": "float", "min": 0.1, "max": 10.0, "description": "Multiplies how quickly collection objects respawn."},
    {"name": "EnemyDropItemRate", "category": "Building and Collection", "type": "float", "min": 0.1, "max": 10.0, "description": "Multiplies the drop rate of items from defeated enemies."},

    # Multiplayer and Server Settings
    {"name": "bIsMultiplay", "category": "Multiplayer and Server", "type": "bool", "description": "Enables multiplayer mode if checked."},
    {"name": "bIsPvP", "category": "Multiplayer and Server", "type": "bool", "description": "Enables player vs. player combat if checked."},
    {"name": "ServerName", "category": "Multiplayer and Server", "type": "string", "description": "Sets the name of the server."},
    {"name": "ServerDescription", "category": "Multiplayer and Server", "type": "string", "description": "Sets a description for the server."},
    {"name": "AdminPassword", "category": "Multiplayer and Server", "type": "string", "description": "Sets the admin password for server management."},
    {"name": "ServerPassword", "category": "Multiplayer and Server", "type": "string", "description": "Sets a password required to join the server."},
    {"name": "PublicPort", "category": "Multiplayer and Server", "type": "int", "min": 1, "max": 65535, "description": "Sets the public port number for the server."},
    {"name": "PublicIP", "category": "Multiplayer and Server", "type": "string", "description": "Sets the public IP address for the server."},
    {"name": "EpicApp", "category": "Multiplayer and Server", "type": "string", "description": "Sets the Epic App identifier for the server."},
    {"name": "RCONEnabled", "category": "Multiplayer and Server", "type": "bool", "description": "Enables RCON for remote server administration if checked."},
    {"name": "RCONPort", "category": "Multiplayer and Server", "type": "int", "min": 1, "max": 65535, "description": "Sets the port number for RCON access."},
    {"name": "Region", "category": "Multiplayer and Server", "type": "string", "description": "Sets the region for the server."},
    {"name": "bUseAuth", "category": "Multiplayer and Server", "type": "bool", "description": "Enables authentication for player logins if checked."},
    {"name": "BanListURL", "category": "Multiplayer and Server", "type": "string", "description": "Sets the URL for the server's ban list."},
    {"name": "CoopPlayerMaxNum", "category": "Multiplayer and Server", "type": "int", "min": 1, "max": 32, "description": "Sets the maximum number of players in co-op mode."},
    {"name": "ServerPlayerMaxNum", "category": "Multiplayer and Server", "type": "int", "min": 1, "max": 32, "description": "Sets the maximum number of players on the server."},
    {"name": "GuildPlayerMaxNum", "category": "Multiplayer and Server", "type": "int", "min": 1, "max": 100, "description": "Sets the maximum number of players in a guild."},
    {"name": "BaseCampMaxNum", "category": "Multiplayer and Server", "type": "int", "min": 0, "max": 1000, "description": "Sets the maximum number of base camps allowed."},
    {"name": "BaseCampWorkerMaxNum", "category": "Multiplayer and Server", "type": "int", "min": 0, "max": 100, "description": "Sets the maximum number of workers per base camp."},
    {"name": "bCanPickupOtherGuildDeathPenaltyDrop", "category": "Multiplayer and Server", "type": "bool", "description": "Allows picking up death penalty drops from other guilds if checked."},
    {"name": "bEnableDefenseOtherGuildPlayer", "category": "Multiplayer and Server", "type": "bool", "description": "Enables defense against other guild players if checked."},
    {"name": "bAutoResetGuildNoOnlinePlayers", "category": "Multiplayer and Server", "type": "bool", "description": "Resets guilds automatically when no players are online if checked."},
    {"name": "AutoResetGuildTimeNoOnlinePlayers", "category": "Multiplayer and Server", "type": "float", "min": 0.0, "max": 168.0, "description": "Sets the time in hours before resetting guilds with no online players."},
    {"name": "bExistPlayerAfterLogout", "category": "Multiplayer and Server", "type": "bool", "description": "Keeps players in the world after logout if checked."},

    # Miscellaneous Settings
    {"name": "DeathPenalty", "category": "Miscellaneous", "type": "enum", "options": ["None", "Item", "ItemAndEquipment", "All"], "description": "Sets the penalty applied when a player dies."},
    {"name": "bEnablePlayerToPlayerDamage", "category": "Miscellaneous", "type": "bool", "description": "Enables damage between players if checked."},
    {"name": "bEnableFriendlyFire", "category": "Miscellaneous", "type": "bool", "description": "Enables damage to allies if checked."},
    {"name": "bEnableInvaderEnemy", "category": "Miscellaneous", "type": "bool", "description": "Enables invader enemies if checked."},
    {"name": "bActiveUNKO", "category": "Miscellaneous", "type": "bool", "description": "Activates the UNKO feature if checked (purpose unclear, possibly debug-related)."},
    {"name": "bEnableAimAssistPad", "category": "Miscellaneous", "type": "bool", "description": "Enables aim assist for controllers if checked."},
    {"name": "bEnableAimAssistKeyboard", "category": "Miscellaneous", "type": "bool", "description": "Enables aim assist for keyboard if checked."},
    {"name": "DropItemMaxNum", "category": "Miscellaneous", "type": "int", "min": 0, "max": 10000, "description": "Sets the maximum number of items that can be dropped on the ground."},
    {"name": "DropItemMaxNum_UNKO", "category": "Miscellaneous", "type": "int", "min": 0, "max": 10000, "description": "Sets the maximum number of UNKO items that can be dropped."},
    {"name": "DropItemAliveMaxHours", "category": "Miscellaneous", "type": "float", "min": 0.0, "max": 24.0, "description": "Sets how long dropped items persist in hours."},
    {"name": "PalEggDefaultHatchingTime", "category": "Miscellaneous", "type": "float", "min": 0.0, "max": 100.0, "description": "Sets the default time in hours for Pal eggs to hatch."},
    {"name": "WorkSpeedRate", "category": "Miscellaneous", "type": "float", "min": 0.1, "max": 10.0, "description": "Multiplies the speed at which work tasks are completed."},
    {"name": "bEnableNonLoginPenalty", "category": "Miscellaneous", "type": "bool", "description": "Applies a penalty for not logging in if checked."},
    {"name": "bEnableFastTravel", "category": "Miscellaneous", "type": "bool", "description": "Enables fast travel between locations if checked."},
    {"name": "bIsStartLocationSelectByMap", "category": "Miscellaneous", "type": "bool", "description": "Allows selecting the starting location via the map if checked."},
]

# Function to parse the PalWorldSettings.ini file
def parse_settings(file_path):
    """Reads the INI file and extracts settings from the OptionSettings line."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    match = re.search(r'OptionSettings=\((.*?)\)', content, re.DOTALL)
    if not match:
        raise ValueError("Invalid INI file format")
    settings_str = match.group(1)
    pairs = settings_str.split(',')
    settings = {}
    for pair in pairs:
        if '=' in pair:
            key, value = pair.split('=', 1)
            key = key.strip()
            value = value.strip()
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]  # Remove quotes from strings
            settings[key] = value
    return settings

# Function to save settings back to the INI file
def save_settings_to_file(file_path, settings):
    """Writes the updated settings back to the INI file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    def replace_settings(match):
        settings_str = ', '.join([f"{k}={v}" for k, v in settings.items()])
        return f'OptionSettings=({settings_str})'
    new_content = re.sub(r'OptionSettings=\(.*?\)', replace_settings, content, flags=re.DOTALL)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

# Main window class for the settings editor
class PalWorldSettingsEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # Set window properties
        self.setWindowTitle("PalWorld Settings Editor")
        self.resize(1000, 700)  # Larger initial window size
        
        # Center the window on screen
        screen_geometry = QGuiApplication.primaryScreen().availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
        
        # Set up the main layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Create search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("Search Settings:")
        search_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type to search settings...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self.filter_settings)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        main_layout.addLayout(search_layout)
        
        # Create tabbed interface with scroll areas for each tab
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.tabs.setTabShape(QTabWidget.TabShape.Rounded)
        self.tabs.setDocumentMode(True)
        self.tabs.setMovable(True)
        
        # Tab icons dictionary (placeholder for now)
        tab_icons = {
            "General": "⚙️",
            "Damage and Health": "❤️",
            "Building and Collection": "🏗️",
            "Multiplayer and Server": "🌐",
            "Miscellaneous": "🔧"
        }
        
        # Store widgets for each setting
        self.setting_widgets = {}
        self.category_widgets = {}
        
        # Create widgets for each category
        categories = sorted(set(setting['category'] for setting in settings_definitions))
        for category in categories:
            # Create scroll area for the tab
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            
            # Container widget for the scroll area
            container = QWidget()
            scroll.setWidget(container)
            
            # Layout for the container
            layout = QVBoxLayout(container)
            layout.setSpacing(15)
            layout.setContentsMargins(15, 15, 15, 15)
            
            # Group settings by subcategories if wanted
            settings_in_category = [s for s in settings_definitions if s['category'] == category]
            
            # Create a form for this category
            form_group = QGroupBox(f"{category} Settings")
            form_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
            form_layout = QFormLayout(form_group)
            form_layout.setSpacing(12)
            form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
            form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
            
            # Add settings to the form
            for setting in settings_in_category:
                # Create label with description tooltip
                label = QLabel(setting['name'])
                label.setToolTip(setting['description'])
                label.setStatusTip(setting['description'])
                label.setFont(QFont("Arial", 10))
                
                # Create appropriate widget based on setting type
                if setting['type'] == 'float':
                    widget = QDoubleSpinBox()
                    widget.setRange(setting.get('min', 0.0), setting.get('max', 100.0))
                    widget.setSingleStep(0.1)
                    widget.setDecimals(2)  # More user-friendly precision
                    widget.setFixedWidth(150)
                    widget.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.PlusMinus)
                    widget.setStatusTip(setting['description'])
                elif setting['type'] == 'int':
                    widget = QSpinBox()
                    widget.setRange(setting.get('min', 0), setting.get('max', 10000))
                    widget.setFixedWidth(150)
                    widget.setButtonSymbols(QSpinBox.ButtonSymbols.PlusMinus)
                    widget.setStatusTip(setting['description'])
                elif setting['type'] == 'bool':
                    widget = QCheckBox()
                    widget.setStatusTip(setting['description'])
                elif setting['type'] == 'string':
                    widget = QLineEdit()
                    widget.setMaxLength(255)
                    widget.setStatusTip(setting['description'])
                elif setting['type'] == 'enum':
                    widget = QComboBox()
                    widget.addItems(setting['options'])
                    widget.setFixedWidth(150)
                    widget.setStatusTip(setting['description'])
                
                # Create a horizontal layout to hold the widget and a reset button
                widget_layout = QHBoxLayout()
                widget_layout.addWidget(widget)
                
                # Add a reset button for each setting
                if setting['type'] in ['float', 'int']:
                    reset_btn = QPushButton("Reset")
                    reset_btn.setFixedWidth(60)
                    reset_btn.setToolTip(f"Reset to default value")
                    reset_btn.clicked.connect(lambda checked, w=widget, s=setting: self.reset_setting(w, s))
                    widget_layout.addWidget(reset_btn)
                
                # Add the widget layout to the form
                form_layout.addRow(label, widget_layout)
                
                # Store the widget for later access
                self.setting_widgets[setting['name']] = widget
            
            # Add the form group to the layout
            layout.addWidget(form_group)
            layout.addStretch(1)  # Add stretch at the bottom
            
            # Add tab with icon
            self.tabs.addTab(scroll, f"{tab_icons.get(category, '🔸')} {category}")
            
            # Store the form group for filtering
            self.category_widgets[category] = form_group
        
        # Add the tabs to the main layout
        main_layout.addWidget(self.tabs)
        
        # Create button row at the bottom
        button_layout = QHBoxLayout()
        
        # Load button
        self.load_button = QPushButton("Load Settings")
        self.load_button.setIcon(QIcon.fromTheme("document-open"))
        self.load_button.clicked.connect(self.load_settings)
        self.load_button.setFixedHeight(40)
        
        # Save button
        self.save_button = QPushButton("Save Settings")
        self.save_button.setIcon(QIcon.fromTheme("document-save"))
        self.save_button.clicked.connect(self.save_settings)
        self.save_button.setFixedHeight(40)
        
        # Reset all button
        self.reset_all_button = QPushButton("Reset All")
        self.reset_all_button.setIcon(QIcon.fromTheme("edit-undo"))
        self.reset_all_button.clicked.connect(self.reset_all_settings)
        self.reset_all_button.setFixedHeight(40)
        
        # Help button
        self.help_button = QPushButton("Help")
        self.help_button.setIcon(QIcon.fromTheme("help-contents"))
        self.help_button.clicked.connect(self.show_help)
        self.help_button.setFixedHeight(40)
        
        # Add buttons to layout
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.reset_all_button)
        button_layout.addWidget(self.help_button)
        
        main_layout.addLayout(button_layout)
        
        self.setCentralWidget(main_widget)
        
        # Create a status bar with permanent widgets
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        
        # File status label
        self.file_status = QLabel("No file loaded")
        status_bar.addPermanentWidget(self.file_status)
        
        # Show initial status message
        self.statusBar().showMessage("Ready to load PalWorld settings. Click 'Load Settings' to begin.")
        
        # Apply stylesheet
        self.apply_stylesheet()
        
    def apply_stylesheet(self):
        """Apply a modern stylesheet to the application"""
        stylesheet = """
        QMainWindow {
            background-color: #f0f0f0;
        }
        
        QTabWidget::pane {
            border: 1px solid #cccccc;
            background-color: #ffffff;
            border-radius: 5px;
        }
        
        QTabBar::tab {
            background-color: #e0e0e0;
            border: 1px solid #cccccc;
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            padding: 8px 12px;
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background-color: #ffffff;
            border-bottom: 1px solid #ffffff;
        }
        
        QTabBar::tab:hover:!selected {
            background-color: #e8e8e8;
        }
        
        QGroupBox {
            border: 1px solid #cccccc;
            border-radius: 5px;
            margin-top: 20px;
            padding-top: 25px;
            background-color: #fafafa;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 5px 15px;
            background-color: #4a86e8;
            color: white;
            border-radius: 3px;
        }
        
        QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
            padding: 5px;
            border: 1px solid #cccccc;
            border-radius: 3px;
            background-color: white;
        }
        
        QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
            border: 1px solid #4a86e8;
        }
        
        QPushButton {
            background-color: #4a86e8;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #3a76d8;
        }
        
        QPushButton:pressed {
            background-color: #2a66c8;
        }
        
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
        }
        
        QScrollArea {
            border: none;
        }
        
        QLabel {
            color: #333333;
        }
        
        QStatusBar {
            background-color: #f0f0f0;
            color: #666666;
        }
        """
        self.setStyleSheet(stylesheet)
        
    def filter_settings(self, text):
        """Filter settings based on search text"""
        search_text = text.lower()
        
        # For each setting, check if it matches search
        for setting in settings_definitions:
            widget = self.setting_widgets.get(setting['name'])
            
            # Skip if widget not found
            if not widget:
                continue
                
            # Get the parent layout (QFormLayout)
            layout = widget.parentWidget().layout()
            if not layout:
                continue
                
            # Check if any part of the setting matches the search
            matches = (
                search_text in setting['name'].lower() or
                search_text in setting['description'].lower() or
                search_text in setting['category'].lower()
            )
                
            # If Type enum, also check the options
            if setting['type'] == 'enum' and 'options' in setting:
                if any(search_text in option.lower() for option in setting['options']):
                    matches = True
                    
            # Show or hide the row based on match
            parent_item = widget.parentWidget().parentWidget()  # Get the QFormLayout row
            if parent_item:
                parent_item.setVisible(matches or not search_text)
        
        # If search is empty, make sure all are visible
        if not search_text:
            for widget in self.setting_widgets.values():
                parent_item = widget.parentWidget().parentWidget()
                if parent_item:
                    parent_item.setVisible(True)
    
    def reset_setting(self, widget, setting):
        """Reset a specific setting to its default value"""
        if setting['type'] == 'float':
            default_value = 1.0  # Assuming default is 1.0 for most multipliers
            widget.setValue(default_value)
        elif setting['type'] == 'int':
            default_value = setting.get('min', 0)  # Use min as default for integers
            widget.setValue(default_value)
        
        # Show brief status message
        self.statusBar().showMessage(f"Reset {setting['name']} to default value", 3000)
            
    def reset_all_settings(self):
        """Reset all settings to their default values"""
        reply = QMessageBox.question(
            self, 
            "Reset All Settings", 
            "Are you sure you want to reset all settings to their default values?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            for setting in settings_definitions:
                widget = self.setting_widgets.get(setting['name'])
                if not widget:
                    continue
                    
                if setting['type'] == 'float':
                    widget.setValue(1.0)  # Default is usually 1.0 for multipliers
                elif setting['type'] == 'int':
                    widget.setValue(setting.get('min', 0))
                elif setting['type'] == 'bool':
                    widget.setChecked(False)
                elif setting['type'] == 'string':
                    widget.setText("")
                elif setting['type'] == 'enum' and 'options' in setting and setting['options']:
                    widget.setCurrentIndex(0)
                    
            self.statusBar().showMessage("All settings reset to default values", 5000)
            
    def show_help(self):
        """Show help dialog with information about settings"""
        help_dialog = QMessageBox(self)
        help_dialog.setWindowTitle("PalWorld Settings Editor - Help")
        help_dialog.setIcon(QMessageBox.Icon.Information)
        
        help_text = """
        <h2>PalWorld Settings Editor Help</h2>
        
        <h3>Getting Started</h3>
        <p>1. Click <b>Load Settings</b> to open your PalWorldSettings.ini file</p>
        <p>2. Adjust the settings using the various tabs and controls</p>
        <p>3. Click <b>Save Settings</b> to save your changes back to the file</p>
        
        <h3>Tips</h3>
        <ul>
            <li>Use the search bar to quickly find specific settings</li>
            <li>Hover over any setting to see a description tooltip</li>
            <li>Use the Reset buttons to restore default values</li>
            <li>Settings are organized into tabs by category</li>
        </ul>
        
        <h3>Common Settings</h3>
        <ul>
            <li><b>ExpRate</b>: Increase to make leveling faster</li>
            <li><b>PalCaptureRate</b>: Increase to make catching Pals easier</li>
            <li><b>DayTimeSpeedRate / NightTimeSpeedRate</b>: Adjust day/night cycle speed</li>
        </ul>
        """
        
        help_dialog.setText(help_text)
        help_dialog.setTextFormat(Qt.TextFormat.RichText)
        help_dialog.exec()

    def load_settings(self):
        """Loads settings from a selected PalWorldSettings.ini file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Load PalWorldSettings.ini", 
            "", 
            "INI files (*.ini);;All files (*.*)"
        )
        
        if not file_path:
            return
            
        try:
            # Show loading in status bar
            self.statusBar().showMessage("Loading settings...")
            
            # Parse the settings
            settings = parse_settings(file_path)
            
            # Update all widgets with the loaded values
            for setting in settings_definitions:
                if setting['name'] in settings:
                    value = settings[setting['name']]
                    widget = self.setting_widgets[setting['name']]
                    
                    if setting['type'] == 'float':
                        widget.setValue(float(value))
                    elif setting['type'] == 'int':
                        widget.setValue(int(value))
                    elif setting['type'] == 'bool':
                        widget.setChecked(value.lower() == 'true')
                    elif setting['type'] == 'string':
                        widget.setText(value)
                    elif setting['type'] == 'enum':
                        widget.setCurrentText(value)
                        
            # Store path and update UI
            self.file_path = file_path
            self.file_status.setText(f"Loaded: {os.path.basename(file_path)}")
            self.statusBar().showMessage("Settings loaded successfully", 5000)
            
            # Show a success message
            QMessageBox.information(
                self, 
                "Settings Loaded", 
                f"Successfully loaded settings from:\n{file_path}"
            )
            
        except Exception as e:
            self.statusBar().showMessage("Error loading settings")
            QMessageBox.critical(
                self, 
                "Error Loading Settings", 
                f"Failed to load settings from the file:\n{str(e)}"
            )

    def save_settings(self):
        """Saves the current settings back to the loaded INI file."""
        if not hasattr(self, 'file_path'):
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Save PalWorldSettings.ini", 
                "", 
                "INI files (*.ini);;All files (*.*)"
            )
            if not file_path:
                return
            self.file_path = file_path
            
        try:
            # Show saving in status bar
            self.statusBar().showMessage("Saving settings...")
            
            # Collect all settings from widgets
            settings = {}
            for setting in settings_definitions:
                widget = self.setting_widgets[setting['name']]
                
                if setting['type'] == 'float':
                    value = str(widget.value())
                elif setting['type'] == 'int':
                    value = str(widget.value())
                elif setting['type'] == 'bool':
                    value = "True" if widget.isChecked() else "False"
                elif setting['type'] == 'string':
                    value = f'"{widget.text()}"'  # Add quotes for strings
                elif setting['type'] == 'enum':
                    value = widget.currentText()
                    
                settings[setting['name']] = value
                
            # Save to file
            save_settings_to_file(self.file_path, settings)
            
            # Update status
            self.file_status.setText(f"Saved: {os.path.basename(self.file_path)}")
            self.statusBar().showMessage("Settings saved successfully", 5000)
            
            # Show success message
            QMessageBox.information(
                self, 
                "Settings Saved", 
                f"Successfully saved settings to:\n{self.file_path}"
            )
            
        except Exception as e:
            self.statusBar().showMessage("Error saving settings")
            QMessageBox.critical(
                self, 
                "Error Saving Settings", 
                f"Failed to save settings to the file:\n{str(e)}"
            )
            
# Main application entry point
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for a modern look
    window = PalWorldSettingsEditor()
    window.show()
    sys.exit(app.exec())