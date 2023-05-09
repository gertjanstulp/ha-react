import voluptuous as vol

from importlib import import_module

from custom_components.react.base import ReactBase
from custom_components.react.plugin.api import HassApi, PluginApi
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData

_LOGGER = get_react_logger()


class PluginBase():
    def __init__(self, schema: vol.Schema = None) -> None:
        self.schema = schema or vol.Schema({})


    def validate(self, config: DynamicData) -> bool:
        return True


    def load(self, plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
        raise NotImplementedError()


class PluginFactory:
    def __init__(self, react: ReactBase) -> None:
        self._react = react
        self.plugin_api = PluginApi(react)
        self.hass_api = HassApi(react.hass)


    def load_plugins(self):
        for plugin_config in self._react.configuration.plugin_config.plugins:
            try:
                plugin_module = import_module(f"{plugin_config.module}.plugin")
                if not hasattr(plugin_module, "Plugin"):
                    _LOGGER.error(f"PluginFactory - Invalid plugin configuration: Plugin class not found in '{plugin_module}'")
                
                plugin: PluginBase = plugin_module.Plugin()
                if not plugin:
                    _LOGGER.error(f"PluginFactory - Invalid plugin configuration: Plugin class in '{plugin_module}' is not a valid class")

                config = plugin_config.config.source if plugin_config.config else {}
                if plugin.schema is not None:
                    try:
                        config = plugin.schema(config)
                    except vol.MultipleInvalid as mex:
                        for error in mex.errors:
                            _LOGGER.error(f"Configuration for {plugin_config.module} is invalid - {error.error_message}: {error.path[0] if error.path else ''}")
                        continue
                    except vol.Invalid as ex:
                        _LOGGER.exception(f"Configuration for {plugin_config.module} is invalid")
                        continue

                if plugin.validate(plugin_config.config):
                    plugin.load(self.plugin_api, self.hass_api, plugin_config.config)

            except:
                _LOGGER.exception(f"PluginFactory - Could not load plugin '{plugin_config.module}'")
        self._react.task_manager.execute_plugin_tasks()


    def reload(self):
        self.plugin_api.unload_tasks()
        self.load_plugins()
