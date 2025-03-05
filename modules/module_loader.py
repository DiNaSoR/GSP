import os
import re
from pathlib import Path
import importlib.util

class ModuleLoader:
    """
    Class responsible for detecting game type from .ini files and loading the appropriate module
    """
    
    def __init__(self):
        # Path to the modules directory
        self.modules_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Dictionary to store loaded modules
        self.modules = {}
        
        # Load all available modules
        self.discover_modules()
    
    def discover_modules(self):
        """Discover all available game modules in the modules directory"""
        for item in os.listdir(self.modules_dir):
            module_path = os.path.join(self.modules_dir, item)
            
            # Check if it's a directory and contains a module.py file
            if os.path.isdir(module_path) and item != '__pycache__':
                module_file = os.path.join(module_path, 'module.py')
                if os.path.isfile(module_file):
                    try:
                        # Try to load the module
                        self.load_module(item, module_file)
                    except Exception as e:
                        print(f"Error loading module {item}: {str(e)}")
    
    def load_module(self, module_name, module_file):
        """Load a module from its file path"""
        try:
            # Load the module using importlib
            spec = importlib.util.spec_from_file_location(module_name, module_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get the module class
            if hasattr(module, 'GameModule'):
                module_class = getattr(module, 'GameModule')
                module_instance = module_class()
                
                # Store the module instance
                self.modules[module_name] = module_instance
                print(f"Loaded module: {module_name}")
            else:
                print(f"Module {module_name} does not have a GameModule class")
        
        except Exception as e:
            print(f"Error importing module {module_name}: {str(e)}")
            raise
    
    def get_all_modules(self):
        """Return all loaded modules"""
        return self.modules
    
    def detect_game_from_file(self, file_path):
        """
        Detect the game type from an .ini file and return the appropriate module
        Returns a tuple of (game_name, module_instance) or (None, None) if no match
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Get the file name and directory
        file_name = os.path.basename(file_path)
        dir_name = os.path.dirname(file_path)
        
        # Read the first few lines of the file to check content
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            try:
                content_sample = f.read(2048)  # Read first 2KB for pattern matching
            except Exception:
                content_sample = ""
        
        # Try each module's detection rules
        for module_name, module in self.modules.items():
            if hasattr(module, 'detect_game') and callable(module.detect_game):
                if module.detect_game(file_path, file_name, dir_name, content_sample):
                    return module.get_game_name(), module
        
        # No specific module detected
        return None, None 