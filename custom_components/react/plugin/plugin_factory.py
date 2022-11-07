from __future__ import annotations

from importlib import import_module

from custom_components.react.base import ReactBase
from custom_components.react.tasks.defaults.default_task import DefaultTask


class PluginApi():
    def __init__(self, react: ReactBase) -> None:
        self.react = react


    def register_default_task(self, task_type: type[DefaultTask], **kwargs):
        self.react.task_manager.start_task(task_type(self.react, **kwargs))


class PluginFactory:
    def __init__(self, react: ReactBase) -> None:
        self.react = react
        self.api = PluginApi(react)


    def load_plugins(self):
        for plugin_name in self.react.configuration.plugin_config.plugins:
            plugin_module = import_module(plugin_name)
            if not hasattr(plugin_module, "setup_plugin"):
                raise Exception(f"Invalid plugin configuration: setup_plugin method missing in {plugin_name}")
            plugin_module.setup_plugin(plugin_api=self.api)