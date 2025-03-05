import configparser
import os
import json
import re
from pathlib import Path
import sys
import time
from datetime import datetime

# Add parent directory to path for importing base module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_module import BaseModule

class GameModule(BaseModule):
    """
    Palworld game module that defines settings specific to Palworld.
    """
    
    def __init__(self):
        # Load the settings definitions
        module_dir = os.path.dirname(os.path.abspath(__file__))
        self.module_dir = module_dir
        settings_json_path = os.path.join(module_dir, 'settings.json')
        
        try:
            with open(settings_json_path, 'r', encoding='utf-8') as f:
                self.settings_definitions = json.load(f)
        except FileNotFoundError:
            # If settings.json doesn't exist, use hardcoded definitions
            self.settings_definitions = self._get_hardcoded_settings()
            
            # Save the hardcoded settings to a JSON file for future use
            try:
                # Create settings.json if it doesn't exist
                with open(settings_json_path, 'w', encoding='utf-8') as f:
                    json.dump(self.settings_definitions, f, indent=2)
                print(f"Created settings.json at {settings_json_path}")
            except Exception as e:
                print(f"Warning: Could not save settings to JSON: {str(e)}")
        
        # Compile regex patterns for performance
        self.options_pattern = re.compile(r'OptionSettings=\((.*?)\)', re.DOTALL)
        self.key_value_pattern = re.compile(r'(\w+)=(.*?)(?:,|\s*$)', re.DOTALL)
    
    def get_game_name(self):
        """Return the name of the game this module is for"""
        return "Palworld"
    
    def detect_game(self, file_path, file_name, dir_name, content_sample):
        """
        Detect if an .ini file is for Palworld
        
        Returns:
            bool: True if the file is detected as belonging to Palworld, False otherwise
        """
        # First try using a more efficient regex pattern for detection
        palworld_patterns = [
            r'/Script/Pal\.PalGameWorldSettings',
            r'OptionSettings=\(',
            r'DayTimeSpeedRate=[0-9\.]+',
            r'PalCaptureRate=[0-9\.]+'
        ]
        
        # Try to match any of the patterns
        for pattern in palworld_patterns:
            if re.search(pattern, content_sample):
                return True
        
        # Check file name
        if file_name.lower() == "palworldsettings.ini":
            return True
            
        # Check directory name for clues
        dir_basename = os.path.basename(dir_name).lower()
        if "palworld" in dir_basename or "pal" in dir_basename:
            # Look for common Palworld settings in content
            common_settings = ["ExpRate", "DeathPenalty", "BaseCampMaxNum"]
            for setting in common_settings:
                if setting in content_sample:
                    return True
        
        return False
    
    def get_all_settings(self):
        """Return all settings definitions"""
        return self.settings_definitions
    
    def get_categories(self):
        """Return a list of categories for the settings"""
        categories = set()
        for setting in self.settings_definitions:
            if 'category' in setting:
                categories.add(setting['category'])
        
        return sorted(list(categories))
    
    def get_settings_by_category(self, category):
        """Return settings for a specific category"""
        return [s for s in self.settings_definitions if s.get('category') == category]
    
    def get_default_settings(self):
        """Return default values for all settings"""
        defaults = {}
        for setting in self.settings_definitions:
            defaults[setting['name']] = setting.get('default', '')
        return defaults
    
    def parse_ini_file(self, file_path):
        """
        Parse a Palworld .ini file and return its settings
        
        Palworld uses a custom format that's not standard .ini, so we need custom parsing.
        """
        # First, try to parse using regular configparser as a fallback
        config = configparser.ConfigParser(allow_no_value=True, interpolation=None)
        config.optionxform = str  # Preserve case
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # Use regex for the main parsing since Palworld has a non-standard format
            options_match = self.options_pattern.search(content)
            if not options_match:
                # Try normal configparser as fallback
                config.read(file_path)
                
                # Convert configparser format to our settings format
                settings_data = {}
                for section in config.sections():
                    for option in config[section]:
                        key_name = option  # Use just the option name as the key
                        settings_data[key_name] = config[section][option]
                        
                return settings_data
            
            # Extract the options block using the matched pattern
            options_block = options_match.group(1)
            
            # Create a settings dictionary
            settings_data = {}
            
            # Use regex to find all key=value pairs in one go
            for match in self.key_value_pattern.finditer(options_block):
                key = match.group(1).strip()
                value = match.group(2).strip()
                
                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                
                settings_data[key] = value
            
            # If no settings were found, try to parse line by line
            if not settings_data:
                for line in options_block.split('\n'):
                    line = line.strip()
                    if '=' in line:
                        parts = line.split('=', 1)
                        if len(parts) == 2:
                            key = parts[0].strip()
                            value = parts[1].strip()
                            
                            # Remove trailing comma if present
                            if value.endswith(','):
                                value = value[:-1].strip()
                                
                            # Remove quotes if present
                            if value.startswith('"') and value.endswith('"'):
                                value = value[1:-1]
                                
                            settings_data[key] = value
            
            # Create backup of original file
            self._create_backup(file_path)
            
            # Debug log the parsed settings
            log_path = os.path.join(self.module_dir, 'parse_log.txt')
            with open(log_path, 'a') as f:
                f.write(f"{datetime.now()} - Parsed {file_path}, found {len(settings_data)} settings\n")
                for key, value in settings_data.items():
                    f.write(f"  {key} = {value}\n")
            
            return settings_data
            
        except Exception as e:
            # Log the error
            error_log_path = os.path.join(self.module_dir, 'error_log.txt')
            with open(error_log_path, 'a') as f:
                f.write(f"{datetime.now()} - Error parsing {file_path}: {str(e)}\n")
            raise ValueError(f"Failed to parse Palworld .ini file: {str(e)}")
    
    def save_ini_file(self, file_path, settings):
        """
        Save settings to a Palworld .ini file
        
        Args:
            file_path (str): Path to the .ini file
            settings (dict): Dictionary of setting names to their values
        """
        try:
            # Create backup before saving
            self._create_backup(file_path)
            
            # Read the original file
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # Find the OptionSettings block
            options_match = self.options_pattern.search(content)
            if not options_match:
                raise ValueError("Could not find OptionSettings in the Palworld .ini file")
            
            # Build a new options block
            new_options = []
            
            # Add each setting in a specific order
            for setting_def in self.settings_definitions:
                name = setting_def['name']
                
                if name in settings:
                    value = settings[name]
                    
                    # Format based on type
                    if setting_def['type'] == 'string' and not value.startswith('"'):
                        value = f'"{value}"'
                    
                    new_options.append(f"    {name}={value}")
            
            # Join with commas and newlines
            new_options_block = ",\n".join(new_options)
            
            # Replace the old options block
            new_content = content[:options_match.start(1)] + "\n" + new_options_block + "\n" + content[options_match.end(1):]
            
            # Write the updated content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
            # Log successful save
            log_path = os.path.join(self.module_dir, 'save_log.txt')
            with open(log_path, 'a') as f:
                f.write(f"{datetime.now()} - Successfully saved {file_path}\n")
                
        except Exception as e:
            # Log the error
            error_log_path = os.path.join(self.module_dir, 'error_log.txt')
            with open(error_log_path, 'a') as f:
                f.write(f"{datetime.now()} - Error saving {file_path}: {str(e)}\n")
            raise ValueError(f"Failed to save Palworld .ini file: {str(e)}")
    
    def _create_backup(self, file_path):
        """Create a backup of the ini file before modifying it"""
        try:
            # Create backups directory if it doesn't exist
            backup_dir = os.path.join(self.module_dir, 'backups')
            os.makedirs(backup_dir, exist_ok=True)
            
            # Generate backup filename with timestamp
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            file_name = os.path.basename(file_path)
            backup_name = f"{os.path.splitext(file_name)[0]}_{timestamp}.ini"
            backup_path = os.path.join(backup_dir, backup_name)
            
            # Copy the file
            with open(file_path, 'r', encoding='utf-8', errors='replace') as src:
                with open(backup_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
                    
            return True
        except Exception as e:
            print(f"Warning: Could not create backup: {str(e)}")
            return False

    def _get_hardcoded_settings(self):
        """
        Return hardcoded settings definitions for Palworld.
        This is used if the settings.json file doesn't exist.
        """
        return [
            # General Settings
            {"name": "Difficulty", "category": "General", "type": "enum", "options": ["None", "Casual", "Normal", "Hard"], "default": "None", "description": "Sets the game difficulty level. 'None' uses custom settings."},
            {"name": "DayTimeSpeedRate", "category": "General", "type": "float", "min": 0.1, "max": 10.0, "default": "1.000000", "description": "Adjusts how fast daytime progresses in the game."},
            {"name": "NightTimeSpeedRate", "category": "General", "type": "float", "min": 0.1, "max": 10.0, "default": "1.000000", "description": "Adjusts how fast nighttime progresses in the game."},
            {"name": "ExpRate", "category": "General", "type": "float", "min": 0.1, "max": 100.0, "default": "1.000000", "description": "Multiplies the rate at which players gain experience points."},
            {"name": "PalCaptureRate", "category": "General", "type": "float", "min": 0.1, "max": 10.0, "default": "1.000000", "description": "Multiplies the success rate of capturing Pals."},
            {"name": "PalSpawnNumRate", "category": "General", "type": "float", "min": 0.1, "max": 10.0, "default": "1.000000", "description": "Multiplies the number of Pals that spawn in the world."},
            
            # Damage and Health Settings
            {"name": "PalDamageRateAttack", "category": "Damage and Health", "type": "float", "min": 0.1, "max": 10.0, "default": "1.000000", "description": "Multiplies the attack damage dealt by Pals."},
            {"name": "PalDamageRateDefense", "category": "Damage and Health", "type": "float", "min": 0.1, "max": 10.0, "default": "1.000000", "description": "Multiplies the damage Pals take (defense modifier)."},
            {"name": "PlayerDamageRateAttack", "category": "Damage and Health", "type": "float", "min": 0.1, "max": 10.0, "default": "1.000000", "description": "Multiplies the attack damage dealt by players."},
            {"name": "PlayerDamageRateDefense", "category": "Damage and Health", "type": "float", "min": 0.1, "max": 10.0, "default": "1.000000", "description": "Multiplies the damage players take (defense modifier)."},
            {"name": "PlayerAutoHPRegeneRate", "category": "Damage and Health", "type": "float", "min": 0.1, "max": 10.0, "default": "1.000000", "description": "Multiplies the rate at which players automatically regenerate health."},
            {"name": "PlayerAutoHpRegeneRateInSleep", "category": "Damage and Health", "type": "float", "min": 0.1, "max": 10.0, "default": "1.000000", "description": "Multiplies the rate at which players regenerate health while sleeping."},
            {"name": "PalAutoHPRegeneRate", "category": "Damage and Health", "type": "float", "min": 0.1, "max": 10.0, "default": "1.000000", "description": "Multiplies the rate at which Pals automatically regenerate health."},
            {"name": "PalAutoHpRegeneRateInSleep", "category": "Damage and Health", "type": "float", "min": 0.1, "max": 10.0, "default": "1.000000", "description": "Multiplies the rate at which Pals regenerate health while in a Palbox."},
            
            # Survival Settings
            {"name": "PlayerStomachDecreaceRate", "category": "Survival", "type": "float", "min": 0.1, "max": 5.0, "default": "1.000000", "description": "Multiplies how quickly players get hungry (higher = get hungry faster)."},
            {"name": "PlayerStaminaDecreaceRate", "category": "Survival", "type": "float", "min": 0.1, "max": 5.0, "default": "1.000000", "description": "Multiplies how quickly players lose stamina (higher = stamina depletes faster)."},
            {"name": "PalStomachDecreaceRate", "category": "Survival", "type": "float", "min": 0.1, "max": 5.0, "default": "1.000000", "description": "Multiplies how quickly Pals get hungry (higher = get hungry faster)."},
            {"name": "PalStaminaDecreaceRate", "category": "Survival", "type": "float", "min": 0.1, "max": 5.0, "default": "1.000000", "description": "Multiplies how quickly Pals lose stamina (higher = stamina depletes faster)."},
            
            # Building and Collection
            {"name": "BuildObjectDamageRate", "category": "Building", "type": "float", "min": 0.1, "max": 5.0, "default": "1.000000", "description": "Multiplies the damage dealt to player-built structures."},
            {"name": "BuildObjectDeteriorationDamageRate", "category": "Building", "type": "float", "min": 0.0, "max": 5.0, "default": "1.000000", "description": "Multiplies the rate at which player-built structures deteriorate."},
            {"name": "CollectionDropRate", "category": "Collection", "type": "float", "min": 0.1, "max": 10.0, "default": "1.000000", "description": "Multiplies the amount of resources dropped when harvesting."},
            {"name": "CollectionObjectHpRate", "category": "Collection", "type": "float", "min": 0.1, "max": 10.0, "default": "1.000000", "description": "Multiplies the health of harvestable objects."},
            {"name": "CollectionObjectRespawnSpeedRate", "category": "Collection", "type": "float", "min": 0.1, "max": 10.0, "default": "1.000000", "description": "Multiplies how quickly harvestable objects respawn."},
            {"name": "EnemyDropItemRate", "category": "Collection", "type": "float", "min": 0.1, "max": 10.0, "default": "1.000000", "description": "Multiplies the amount of items dropped by enemies."},
            
            # Multiplayer and PvP
            {"name": "DeathPenalty", "category": "Multiplayer", "type": "enum", "options": ["None", "Item", "ItemAndEquipment", "All"], "default": "All", "description": "Sets what items are dropped on player death."},
            {"name": "bEnablePlayerToPlayerDamage", "category": "Multiplayer", "type": "boolean", "default": "False", "description": "If enabled, players can damage each other (PvP)."},
            {"name": "bEnableFriendlyFire", "category": "Multiplayer", "type": "boolean", "default": "False", "description": "If enabled, players can damage allied players or guild members."},
            {"name": "bEnableInvaderEnemy", "category": "Multiplayer", "type": "boolean", "default": "True", "description": "If enabled, enemy NPCs will occasionally invade the player's base."},
            {"name": "bEnableAimAssistPad", "category": "Gameplay", "type": "boolean", "default": "True", "description": "Enables aim assist for controller players."},
            {"name": "bEnableAimAssistKeyboard", "category": "Gameplay", "type": "boolean", "default": "False", "description": "Enables aim assist for keyboard and mouse players."},
            
            # Base Camp Settings
            {"name": "BaseCampMaxNum", "category": "BaseBuilding", "type": "integer", "min": 1, "max": 512, "default": "128", "description": "Maximum number of base camps that can be built."},
            {"name": "BaseCampWorkerMaxNum", "category": "BaseBuilding", "type": "integer", "min": 1, "max": 100, "default": "15", "description": "Maximum number of Pals that can be assigned to a single base camp."},
            {"name": "DropItemMaxNum", "category": "BaseBuilding", "type": "integer", "min": 100, "max": 10000, "default": "3000", "description": "Maximum number of dropped items in the world."},
            {"name": "DropItemAliveMaxHours", "category": "BaseBuilding", "type": "float", "min": 0.1, "max": 24.0, "default": "1.000000", "description": "How many hours dropped items remain in the world before despawning."},
            {"name": "bAutoResetGuildNoOnlinePlayers", "category": "Guild", "type": "boolean", "default": "False", "description": "If enabled, guilds with no active players will automatically disband."},
            {"name": "AutoResetGuildTimeNoOnlinePlayers", "category": "Guild", "type": "float", "min": 1.0, "max": 720.0, "default": "72.000000", "description": "Hours after which an inactive guild will disband."},
            {"name": "GuildPlayerMaxNum", "category": "Guild", "type": "integer", "min": 1, "max": 100, "default": "20", "description": "Maximum number of players in a guild."},
            {"name": "PalEggDefaultHatchingTime", "category": "Gameplay", "type": "float", "min": 0.01, "max": 10.0, "default": "0.100000", "description": "Multiplier for how quickly Pal eggs hatch (lower is faster)."},
            {"name": "WorkSpeedRate", "category": "BaseBuilding", "type": "float", "min": 0.1, "max": 10.0, "default": "1.000000", "description": "Multiplies the work speed of Pals assigned to a base."},
            
            # Server Settings
            {"name": "bIsMultiplay", "category": "Server", "type": "boolean", "default": "False", "description": "If enabled, the game is played in multiplayer mode."},
            {"name": "bIsPvP", "category": "Server", "type": "boolean", "default": "False", "description": "If enabled, PvP is enabled on the server."},
            {"name": "bCanPickupOtherGuildDeathPenaltyDrop", "category": "Server", "type": "boolean", "default": "False", "description": "If enabled, players can pick up death drops from players in other guilds."},
            {"name": "bEnableNonLoginPenalty", "category": "Server", "type": "boolean", "default": "False", "description": "If enabled, there's a penalty for not logging in for a certain period."},
            {"name": "bEnableFastTravel", "category": "Server", "type": "boolean", "default": "True", "description": "If enabled, players can use fast travel."},
            {"name": "bIsStartLocationSelectByMap", "category": "Server", "type": "boolean", "default": "True", "description": "If enabled, players can select their starting location on the map."},
            {"name": "bExistPlayerAfterLogout", "category": "Server", "type": "boolean", "default": "False", "description": "If enabled, player characters remain in the world after logging out."},
            {"name": "bEnableDefenseOtherGuildPlayer", "category": "Server", "type": "boolean", "default": "False", "description": "If enabled, players can defend against other guild members."},
            {"name": "CoopPlayerMaxNum", "category": "Server", "type": "integer", "min": 1, "max": 32, "default": "6", "description": "Maximum number of players in a co-op session."},
            {"name": "ServerPlayerMaxNum", "category": "Server", "type": "integer", "min": 1, "max": 255, "default": "32", "description": "Maximum number of players on the server."},
            {"name": "ServerName", "category": "Server", "type": "string", "pattern": r"^[\w\s\-\.]{1,50}$", "default": "\"Palworld Server\"", "description": "The name of the server displayed in the server list."},
            {"name": "ServerDescription", "category": "Server", "type": "string", "default": "\"\"", "description": "A description of the server displayed in the server list."},
            {"name": "AdminPassword", "category": "Server", "type": "string", "default": "\"\"", "description": "Password for admin access to the server."},
            {"name": "ServerPassword", "category": "Server", "type": "string", "default": "\"\"", "description": "Password required to join the server."},
            {"name": "PublicPort", "category": "Server", "type": "integer", "min": 1, "max": 65535, "default": "8211", "description": "Public port used by the server."},
            {"name": "PublicIP", "category": "Server", "type": "string", "pattern": r"^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})?$", "default": "\"\"", "description": "Public IP address of the server."},
            {"name": "RCONEnabled", "category": "Server", "type": "boolean", "default": "False", "description": "If enabled, RCON is allowed for remote server administration."},
            {"name": "RCONPort", "category": "Server", "type": "integer", "min": 1, "max": 65535, "default": "25575", "description": "Port used for RCON."},
            {"name": "Region", "category": "Server", "type": "string", "default": "\"\"", "description": "Region where the server is located."},
            {"name": "bUseAuth", "category": "Server", "type": "boolean", "default": "True", "description": "If enabled, server uses authentication."},
            {"name": "BanListURL", "category": "Server", "type": "string", "pattern": r"^(https?:\/\/[\w\-\.\/]+)?$", "default": "\"https://api.palworldgame.com/api/banlist.txt\"", "description": "URL to the ban list used by the server."}
        ] 