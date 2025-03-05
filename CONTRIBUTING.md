<div align="center">

# 🤝 Contributing to Game Settings Editor

[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)
[![Code of Conduct](https://img.shields.io/badge/code%20of%20conduct-contributor%20covenant-blue.svg)](CODE_OF_CONDUCT.md)

</div>

---

Thank you for your interest in contributing to Game Settings Editor! This document provides guidelines and instructions for contributing to this project. By participating, you are expected to uphold this code of conduct and follow these guidelines.

## 📋 Table of Contents

- [Code of Conduct](#-code-of-conduct)
- [Getting Started](#-getting-started)
- [Development Workflow](#-development-workflow)
- [Pull Request Process](#-pull-request-process)
- [Adding Game Modules](#-adding-game-modules)
- [Coding Standards](#-coding-standards)
- [Testing](#-testing)
- [Documentation](#-documentation)

## 📜 Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/game-settings-editor.git
   cd game-settings-editor
   ```
3. **Set up the development environment**:
   ```bash
   # Create a virtual environment
   python -m venv venv
   
   # Activate the virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```
4. **Create a branch** for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 🔄 Development Workflow

1. **Make your changes** in your feature branch
2. **Run tests** to ensure your changes don't break existing functionality
3. **Commit your changes** with clear, descriptive commit messages:
   ```bash
   git commit -m "Add feature: description of the feature"
   ```
4. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
5. **Submit a pull request** to the main repository

## 📤 Pull Request Process

1. **Update the README.md** with details of changes if applicable
2. **Ensure all tests pass** and your code follows the project's coding standards
3. **Add screenshots** if your changes include UI modifications
4. **Update documentation** if you're changing functionality
5. **Get your PR reviewed** by maintainers
6. **Address review comments** if any are provided

> 💡 **Tip:** Keep your pull requests focused on a single feature or bug fix to simplify the review process.

## 🎮 Adding Game Modules

When adding support for a new game:

1. **Create a new directory** in the `modules` folder with your game's name
2. **Implement the required files**:
   - `__init__.py`: Module initialization
   - `module.py`: Implements the `BaseModule` interface
   - `settings.json`: Defines the game's settings schema

### Module Structure Example

```python
# modules/yourgame/module.py
from modules.base_module import BaseModule

class YourGameModule(BaseModule):
    def __init__(self):
        super().__init__(
            name="Your Game",
            description="Configuration module for Your Game",
            version="1.0.0"
        )
    
    def detect_game(self, file_path):
        # Implement detection logic
        return True if "yourgame" in file_path.lower() else False
    
    # Implement other required methods...
```

## 📏 Coding Standards

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Use meaningful variable and function names
- Write docstrings for all functions, classes, and modules
- Keep functions small and focused on a single task
- Add comments for complex logic

### Code Style Example

```python
def parse_setting(setting_value, setting_type):
    """
    Parse a setting value according to its type.
    
    Args:
        setting_value (str): The raw value from the INI file
        setting_type (str): The type to convert to ('int', 'float', 'bool', 'str')
        
    Returns:
        The parsed value in the appropriate type
        
    Raises:
        ValueError: If the value cannot be parsed to the specified type
    """
    if setting_type == 'int':
        return int(setting_value)
    elif setting_type == 'float':
        return float(setting_value)
    elif setting_type == 'bool':
        return setting_value.lower() in ('true', 'yes', '1', 'on')
    else:
        return setting_value  # Default to string
```

## 🧪 Testing

- Write unit tests for all new functionality
- Ensure all tests pass before submitting a pull request
- Test your changes on different platforms if possible

```bash
# Run all tests
python -m unittest discover tests

# Run a specific test file
python -m unittest tests/test_module.py
```

## 📚 Documentation

- Update documentation for any modified functionality
- Document new features thoroughly
- Include examples where appropriate
- Keep the Wiki up-to-date with any changes

---

<div align="center">
  <sub>Thank you for contributing to Game Settings Editor! ❤️</sub>
</div> 