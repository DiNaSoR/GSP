import configparser
import re

class GenericModule:
    """
    Generic module for handling any .ini file when a specific game module is not available.
    This module provides basic editing capabilities for .ini files without game-specific knowledge.
    """
    
    def __init__(self):
        self._settings_cache = []
        
    def get_game_name(self):
        """Return a generic name for this module"""
        return "Generic INI Editor"
    
    def detect_game(self, file_path, file_name, dir_name, content_sample):
        """This is a fallback module, so it should never detect any specific game"""
        return False
    
    def get_all_settings(self):
        """Return all settings definitions"""
        return self._settings_cache
    
    def get_categories(self):
        """Return a list of categories (sections) from the .ini file"""
        categories = set()
        for setting in self._settings_cache:
            if 'section' in setting:
                categories.add(setting['section'])
        
        return sorted(list(categories))
    
    def get_settings_by_category(self, category):
        """Return settings for a specific category (section)"""
        return [s for s in self._settings_cache if s.get('section') == category]
    
    def get_default_settings(self):
        """Return default values for all settings (empty since we don't know defaults)"""
        defaults = {}
        for setting in self._settings_cache:
            defaults[setting['name']] = setting.get('default', '')
        return defaults
    
    def parse_ini_file(self, file_path):
        """
        Parse an .ini file and return its settings
        
        This detects the structure of the .ini file and creates setting definitions
        dynamically based on what it finds in the file.
        """
        config = configparser.ConfigParser(allow_no_value=True, interpolation=None)
        
        # Preserve case of keys
        config.optionxform = str
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                config.read_file(f)
        except Exception as e:
            # If standard parsing fails, try to read as a raw file
            # and handle custom formats manually
            try:
                return self._parse_custom_ini(file_path)
            except Exception as e2:
                raise ValueError(f"Failed to parse .ini file: {str(e2)}")
        
        # Build settings data from parsed config
        settings_data = {}
        self._settings_cache = []
        
        # For each section in the .ini file
        for section in config.sections():
            # For each option in the section
            for option in config[section]:
                value = config[section][option]
                key_name = f"{section}.{option}"
                
                # Store the value
                settings_data[key_name] = value
                
                # Determine the type of the value
                setting_type = self._determine_type(value)
                
                # Create a setting definition
                setting_def = {
                    'name': key_name,
                    'section': section,
                    'type': setting_type,
                    'default': value,
                    'description': f"Setting '{option}' in section '{section}'"
                }
                
                # For numeric types, set reasonable min/max
                if setting_type == 'integer':
                    setting_def['min'] = -2147483647
                    setting_def['max'] = 2147483647
                elif setting_type == 'float':
                    setting_def['min'] = -1000000.0
                    setting_def['max'] = 1000000.0
                
                # Store the setting definition
                self._settings_cache.append(setting_def)
        
        return settings_data
    
    def _parse_custom_ini(self, file_path):
        """
        Parse an .ini file that doesn't conform to the standard format
        This is a fallback for files that configparser can't handle
        """
        settings_data = {}
        self._settings_cache = []
        
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        # Try to identify sections and key-value pairs
        # This is a simplified parser for non-standard .ini files
        current_section = "General"
        
        # First, look for sections [SectionName]
        section_matches = re.finditer(r'\[([^\]]+)\]', content)
        section_positions = [(m.group(1), m.start(), m.end()) for m in section_matches]
        
        # If no sections found, treat the whole file as "General" section
        if not section_positions:
            section_positions = [("General", 0, 0)]
        
        # Process each section
        for i, (section, start, end) in enumerate(section_positions):
            # Determine the end of the section
            next_start = section_positions[i+1][1] if i+1 < len(section_positions) else len(content)
            section_content = content[end:next_start]
            
            # Look for key-value pairs (KEY=VALUE)
            for line in section_content.split('\n'):
                line = line.strip()
                if not line or line.startswith('#') or line.startswith(';'):
                    continue
                
                # Try to split on = or :
                if '=' in line:
                    key, value = line.split('=', 1)
                elif ':' in line:
                    key, value = line.split(':', 1)
                else:
                    continue
                
                key = key.strip()
                value = value.strip()
                key_name = f"{section}.{key}"
                
                # Store the value
                settings_data[key_name] = value
                
                # Determine the type of the value
                setting_type = self._determine_type(value)
                
                # Create a setting definition
                setting_def = {
                    'name': key_name,
                    'section': section,
                    'type': setting_type,
                    'default': value,
                    'description': f"Setting '{key}' in section '{section}'"
                }
                
                # For numeric types, set reasonable min/max
                if setting_type == 'integer':
                    setting_def['min'] = -2147483647
                    setting_def['max'] = 2147483647
                elif setting_type == 'float':
                    setting_def['min'] = -1000000.0
                    setting_def['max'] = 1000000.0
                
                # Store the setting definition
                self._settings_cache.append(setting_def)
        
        return settings_data
    
    def _determine_type(self, value):
        """Determine the type of a value from the .ini file"""
        value = value.strip()
        
        # Check for boolean
        if value.lower() in ('true', 'false', 'yes', 'no', '1', '0'):
            return 'boolean'
        
        # Check for integer
        try:
            int(value)
            return 'integer'
        except ValueError:
            pass
        
        # Check for float
        try:
            float(value)
            return 'float'
        except ValueError:
            pass
        
        # Default to string
        return 'string'
    
    def save_ini_file(self, file_path, settings):
        """
        Save settings to an .ini file
        
        Args:
            file_path (str): Path to the .ini file
            settings (dict): Dictionary of setting names to their values
        """
        # Organize settings by section
        sections = {}
        for key, value in settings.items():
            if '.' in key:
                section, option = key.split('.', 1)
                if section not in sections:
                    sections[section] = {}
                sections[section][option] = value
        
        # Create a new configparser
        config = configparser.ConfigParser(allow_no_value=True, interpolation=None)
        config.optionxform = str  # Preserve case
        
        # Add all the sections and options
        for section, options in sections.items():
            config[section] = options
        
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            config.write(f)
        
        # Refresh settings cache based on the file
        self.parse_ini_file(file_path) 