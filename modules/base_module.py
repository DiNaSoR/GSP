from abc import ABC, abstractmethod

class BaseModule(ABC):
    """
    Abstract base class for game modules.
    All game modules should inherit from this class and implement its methods.
    """
    
    @abstractmethod
    def get_game_name(self):
        """
        Return the name of the game this module is for
        """
        pass
    
    @abstractmethod
    def detect_game(self, file_path, file_name, dir_name, content_sample):
        """
        Detect if an .ini file is for this game
        
        Args:
            file_path (str): Full path to the .ini file
            file_name (str): Name of the .ini file
            dir_name (str): Directory of the .ini file
            content_sample (str): First 2KB of the file content for pattern matching
            
        Returns:
            bool: True if the file is detected as belonging to this game, False otherwise
        """
        pass
    
    @abstractmethod
    def get_all_settings(self):
        """
        Return all settings definitions
        
        Returns:
            list: List of setting dictionaries
        """
        pass
    
    @abstractmethod
    def get_categories(self):
        """
        Return a list of categories for the settings
        
        Returns:
            list: List of category names
        """
        pass
    
    @abstractmethod
    def get_settings_by_category(self, category):
        """
        Return settings for a specific category
        
        Args:
            category (str): Category name
            
        Returns:
            list: List of setting dictionaries for the category
        """
        pass
    
    @abstractmethod
    def get_default_settings(self):
        """
        Return default values for all settings
        
        Returns:
            dict: Dictionary of setting names to default values
        """
        pass
    
    @abstractmethod
    def parse_ini_file(self, file_path):
        """
        Parse an .ini file and return its settings
        
        Args:
            file_path (str): Path to the .ini file
            
        Returns:
            dict: Dictionary of setting names to their values
        """
        pass
    
    @abstractmethod
    def save_ini_file(self, file_path, settings):
        """
        Save settings to an .ini file
        
        Args:
            file_path (str): Path to the .ini file
            settings (dict): Dictionary of setting names to their values
        """
        pass 