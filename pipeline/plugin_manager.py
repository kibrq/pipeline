# my_library/plugin_manager.py

# A dictionary to store registered plugins, now supporting any kind of class
_registered_classes = {}

def load_plugins():
    """
    Load plugins from entry points and combine with user-registered classes.
    This function supports any class type, not just subclasses of MyBaseClass.
    """
    import pkg_resources

    for entry_point in pkg_resources.iter_entry_points(group='pipeline.plugins'):
        plugin_class = entry_point.load()
        # Use the entry point name as the key for the class
        _registered_classes[entry_point.name] = plugin_class
    
    return _registered_classes

def register_class(name, class_obj):
    """
    Allows users or plugins to manually register their own classes.
    No subclass restriction; any class can be registered.
    """
    _registered_classes[name] = class_obj

def get_class(name):
    """
    Retrieve a class by name.
    """
    return _registered_classes.get(name)

def get_all_classes():
    """
    Return all registered classes.
    """
    return _registered_classes
