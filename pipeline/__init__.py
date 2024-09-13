# my_library/__init__.py
from my_library.plugin_manager import load_plugins, register_class, get_class, get_all_classes

# Load all available classes (from entry points or custom registration)
_registered_classes = load_plugins()

# Dynamically inject the loaded classes into the module's namespace
globals().update(_registered_classes)

# Expose the register_class function to allow users to add their own classes
__all__ = ['register_class', 'get_class', 'get_all_classes'] + list(_registered_classes.keys())
