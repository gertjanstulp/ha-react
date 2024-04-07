from __future__ import annotations

from typing import Any, Generic, Iterable, TypeVar
from typing_extensions import Protocol
import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.helpers.importlib import async_import_module

from custom_components.react.base import ReactBase
from custom_components.react.const import (
    PACKAGE_NAME, 
    REACT_LOGGER_PLUGIN,
)
from custom_components.react.config.config import Plugin as PluginConfig
from custom_components.react.plugin.base import PluginApiBase, HassApi, Plugin
from custom_components.react.plugin.base import PluginProviderBase
from custom_components.react.tasks.plugin.base import InputBlock, OutputBlock
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData

_LOGGER = get_react_logger(REACT_LOGGER_PLUGIN)

T_config = TypeVar("T_config", bound=DynamicData)


class PluginFactory:
    def __init__(self, react: ReactBase) -> None:
        self._react = react
        self.plugin_register = PluginRegister()
        self.set_hass_api(react.hass)


    def set_hass_api(self, hass: HomeAssistant):
        self.hass_api = HassApi(hass)


    async def async_load_plugins(self):
        for plugin_config in self._react.configuration.plugin_config.plugins:
            try:
                plugin_module = await async_import_module(self._react.hass, f"{plugin_config.module}.setup")
                if not hasattr(plugin_module, "Setup"):
                    _LOGGER.error(f"Invalid plugin configuration: Setup class not found in '{plugin_module}'")
                    continue
                
                try:
                    setup: PluginSetup = plugin_module.Setup()
                    plugin = setup.create_plugin(self.plugin_register, self.hass_api, plugin_config)
                except:
                    _LOGGER.exception("PluginFactory error")
                    if not setup:
                        _LOGGER.error(f"Invalid plugin configuration: Setup class in '{plugin_module}' is not a valid class")
                    continue

                def register_plugin_api(api_type: type[PluginApiBase], **kwargs):
                    plugin._api = api_type(**kwargs)

                def register_plugin_provider(type: type[PluginProviderBase], provider_type: str, provider_name: str, **kwargs):
                    provider = type(**kwargs)
                    plugin._providers.append(provider)
                    self.plugin_register.register_plugin_provider(provider_type, provider_name, provider)

                def register_input_block(block_type: type[InputBlock] | Iterable[type[InputBlock]], **kwargs):
                    if not isinstance(block_type, Iterable): block_type = [block_type]
                    plugin._input_blocks.extend([item(self._react, **kwargs) for item in block_type])

                def register_output_block(block_type: type[OutputBlock] | Iterable[type[OutputBlock]], **kwargs):
                    if not isinstance(block_type, Iterable): block_type = [block_type]
                    plugin._output_blocks.extend([item(self._react, **kwargs) for item in block_type])

                setup.setup()
                setup.setup_api(register_plugin_api)
                setup.setup_provider(register_plugin_provider)
                setup.setup_input_blocks(register_input_block)
                setup.setup_output_blocks(register_output_block)
                
                plugin._build(self.plugin_register.get_provider)
 

            except:
                _LOGGER.exception(f"Could not load plugin '{plugin_config.module}'")
        self._react.task_manager.execute_plugin_tasks()


    def unload_plugins(self):
        self.plugin_register.unload_plugins()


class PluginRegister():
    def __init__(self) -> None:
        self._plugins: list[Plugin] = []
        self._providers: dict[str, dict[str, Any]] = {}


    def register_plugin(self, plugin: Plugin):
        self._plugins.append(plugin)


    def register_plugin_provider(self, provider_type: str, provider_name: str, provider: Any):
        plugin_dict = self._providers.get(provider_type, None)
        if not plugin_dict:
            plugin_dict = {}
            self._providers[provider_type] = plugin_dict
        plugin_dict[provider_name] = provider


    def get_provider(self, provider_type: str, provider_name: str) -> Any:
        result = None
        plugin_dict = self._providers.get(provider_type)
        if plugin_dict:
            if provider_name:
                result = plugin_dict.get(provider_name, None)
        return result
    

    def unload_plugins(self):
        for plugin in self._plugins:
            plugin.unload()
        self._plugins.clear()


class PluginSetup(Generic[T_config]):
    def __init__(self, schema: vol.Schema = None) -> None:
        self.schema = schema
        
        self.module_name = self.__module__.rsplit(".")[-2]
        self._root_logger = get_react_logger(REACT_LOGGER_PLUGIN)
        self.plugin_logger = get_react_logger(f"{REACT_LOGGER_PLUGIN}.{self.module_name}")

        self.plugin: Plugin[T_config] = None

    def create_plugin(self, plugin_register: PluginRegister, hass_api: HassApi, plugin_config: PluginConfig) -> Plugin[T_config]:
        self._root_logger.debug(f"Loading {self.module_name} plugin")
        
        try:
            config_raw = plugin_config.config.source if plugin_config.config else {}
            if config_raw != None and self.schema:
                self.schema(config_raw)
            config = self.setup_config(config_raw)
        except vol.MultipleInvalid as mex:
            for error in mex.errors:
                self._root_logger.error(f"Configuration for {plugin_config.module} is invalid - {error.error_message}: {error.path[0] if error.path else ''}")
            raise vol.SchemaError()
        except vol.Invalid as ex:
            self._root_logger.exception(f"Configuration for {plugin_config.module} is invalid")
            raise vol.SchemaError()
            
        self.plugin = Plugin[T_config](self.module_name, hass_api, config, self.plugin_logger)
        plugin_register.register_plugin(self.plugin)
        return self.plugin
            

    def setup(self):
        pass


    def setup_config(self, raw_config: dict) -> T_config:
        return DynamicData(raw_config)


    def setup_api(self, setup: ApiSetupCallback):
        pass


    def setup_provider(self, setup: ProviderSetupCallback):
        pass
        

    def setup_input_blocks(self, setup: InputBlockSetupCallback):
        pass
    

    def setup_output_blocks(self, setup: OutputBlockSetupCallback):
        pass


class ApiSetupCallback(Protocol):
    def __call__(self, api_type: type[PluginApiBase], **kwargs) -> Any: ...


class ProviderSetupCallback(Protocol):
    def __call__(self, type: type[PluginProviderBase], provider_type: str, provider_name: str, **kwargs) -> Any: ...


class InputBlockSetupCallback(Protocol):
    def __call__(self, type: type[InputBlock] | Iterable[type[InputBlock]], **kwargs): ...


class OutputBlockSetupCallback(Protocol):
    def __call__(self, type: type[OutputBlock] | Iterable[type[OutputBlock]], **kwargs): ...
