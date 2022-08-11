from __future__ import annotations

from importlib import import_module

from .notify_plugin import NotifyPlugin

from ..base import ReactBase


class PluginFactory:
    def __init__(self, react: ReactBase) -> None:
        self.react = react
        self.plugins = {}
        

    def get_notify_plugin(self) -> NotifyPlugin:
        plugin = self.plugins.get("notify", None)
        if not plugin:
            plugin_name = self.react.configuration.plugin_config.notify
            if plugin_name:
                plugin_module = import_module(plugin_name)
                if not hasattr(plugin_module, "setup_plugin"):
                    raise Exception("Invalid plugin configuration: setup_plugin method missing in notify_plugin")
                plugin = plugin_module.setup_plugin(react=self.react)
                self.plugins["notify"] = plugin
        return plugin

