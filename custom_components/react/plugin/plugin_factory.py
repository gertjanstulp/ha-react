from __future__ import annotations

from importlib import import_module

from custom_components.react.base import ReactBase
from custom_components.react.plugin.plugin_api import PluginApi


class PluginFactory:
    def __init__(self, react: ReactBase) -> None:
        self.react = react
        self.api = PluginApi(react)


    def load_plugins(self):
        for plugin_name in self.react.configuration.plugin_config.plugins:
            plugin_module = import_module(plugin_name)
            if not hasattr(plugin_module, "setup_plugin"):
                raise Exception(f"Invalid plugin configuration: setup_plugin method missing in {plugin_name}")
            plugin_module.setup_plugin(api=self.api)