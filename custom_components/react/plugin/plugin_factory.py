from __future__ import annotations

from importlib import import_module
from types import ModuleType
from typing import Any

from custom_components.react.base import ReactBase
from custom_components.react.tasks.plugin.base import PluginTask
from custom_components.react.utils.logger import get_react_logger

_LOGGER = get_react_logger()

class PluginApi():
    def __init__(self, react: ReactBase) -> None:
        self.react = react
        self.tasks: list[PluginTask] = []
        self.services: dict[str, dict[str, Any]] = {}


    def register_plugin_task(self, task_type: type[PluginTask], **kwargs):
        task = task_type(self.react, **kwargs)
        self.react.task_manager.register_task(task)
        self.tasks.append(task)


    def register_plugin_service(self, plugin_name: str, service_type: str, service: Any):
        plugin_dict = self.services.get(plugin_name, None)
        if not plugin_dict:
            plugin_dict = {}
            self.services[plugin_name] = plugin_dict
        plugin_dict[service_type] = service


    def get_service(self, plugin_name: str, service_type: str = None, entity_id: str = None) -> Any:
        result = None
        plugin_dict = self.services.get(plugin_name)
        if plugin_dict:
            if service_type:
                result = plugin_dict.get(service_type, None)
            if not result and entity_id:
                result = plugin_dict.get(entity_id, None)
        return result        


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
                    _LOGGER.error(f"PluginFactory - Invalid plugin configuration: load method missing in '{plugin_module}'")
            except:
                _LOGGER.exception(f"PluginFactory - Could not load plugin '{plugin.module}'")
        self.react.task_manager.execute_plugin_tasks()


    def reload(self):
        self.plugin_api.unload_tasks()
        self.load_plugins()
