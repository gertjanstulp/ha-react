from __future__ import annotations

from importlib import import_module
from types import ModuleType

from custom_components.react.base import ReactBase
from custom_components.react.tasks.plugin.base import PluginTask


class PluginApi():
    def __init__(self, react: ReactBase) -> None:
        self.react = react
        self.tasks: list[PluginTask] = []


    def register_plugin_task(self, task_type: type[PluginTask], **kwargs):
        task = task_type(self.react, **kwargs)
        self.react.task_manager.register_task(task)
        self.tasks.append(task)


    def unload_tasks(self):
        for task in self.tasks:
            self.react.task_manager.unload_task(task)
        self.tasks.clear()


class PluginFactory:
    def __init__(self, react: ReactBase) -> None:
        self.react = react
        self.plugin_api = PluginApi(react)


    def load_plugins(self):
        for plugin in self.react.configuration.plugin_config.plugins:
            try:
                plugin_module = import_module(plugin.module)
                if hasattr(plugin_module, "load"):
                    plugin_module.load(plugin_api=self.plugin_api, config=plugin.config)
                else:
                    self.react.log.error(f"PluginFactory - Invalid plugin configuration: load method missing in '{plugin_module}'")
            except:
                self.react.log.exception(f"PluginFactory - Could not load plugin '{plugin.module}'")
        self.react.task_manager.execute_plugin_tasks()


    def reload(self):
        self.plugin_api.unload_tasks()
        self.load_plugins()
