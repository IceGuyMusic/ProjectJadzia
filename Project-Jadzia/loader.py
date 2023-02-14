""" use a loader for the plugin """

import importlib

class PluginInterface:
    """ A Plugin has a single function """

    @staticmethod
    def initialize()-> None:
        """ initialize the Plugin """

def import_module(name: str) -> PluginInterface:
    return importlib.import_module(name) # type: ignore

def load_plugins(plugins: list[str]) -> None:
    """ Load the plugins defines in the plugin list."""
    for plugin_name in plugins: 
        plugin = import_module(plugin_name)
        plugin.initialize() 
