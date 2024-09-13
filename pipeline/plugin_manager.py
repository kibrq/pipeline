# my_library/plugin_manager.py

# A dictionary to store registered plugins, now supporting any kind of class
_registered_classes = None

def __load_all_plugins(force_reload=False):
    """
    Load plugins from entry points and combine with user-registered classes.
    This function supports any class type, not just subclasses of MyBaseClass.
    """
    import pkg_resources

    global _registered_classes

    if not _registered_classes is None and not force_reload:
        return
        
    _registered_classes = {}

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

def get_class(name, force_reload=False):
    """
    Retrieve a class by name.
    """

    __load_all_plugins(force_reload=force_reload)
    
    return _registered_classes.get(name)

def get_all_classes(name, force_reload=False):
    """
    Return all registered classes.
    """

    __load_all_plugins(force_reload=force_reload)
    
    return _registered_classes
