from .plugin_manager import register_class, get_class, get_all_classes
import pathlib
import yaml

# Custom representer for PosixPath to store it as a string in YAML
def represent_posixpath(dumper, data):
    return dumper.represent_scalar(u'tag:yaml.org,2002:str', str(data))

yaml.add_representer(pathlib.PosixPath, represent_posixpath)

# Load all available classes (from entry points or custom registration)
# _registered_classes = load_plugins()

# Dynamically inject the loaded classes into the module's namespace
# globals().update(_registered_classes)

# Expose the register_class function to allow users to add their own classes
__all__ = ['register_class', 'get_class', 'get_all_classes', 'load_plugins']
