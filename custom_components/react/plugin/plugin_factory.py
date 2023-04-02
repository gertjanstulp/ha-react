from __future__ import annotations
from asyncio import sleep

from importlib import import_module
from typing import Any
from uuid import uuid4

from homeassistant.components.tts.media_source import generate_media_source_id
from homeassistant.core import Context, HomeAssistant, SERVICE_CALL_LIMIT, State
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_registry import RegistryEntry

from custom_components.react.base import ReactBase
from custom_components.react.tasks.plugin.base import PluginTask
from custom_components.react.utils.logger import get_react_logger

_LOGGER = get_react_logger()


class ApiBase():
    def __init__(self, plugin_api: PluginApi, hass_api: HassApi) -> None:
        self.plugin_api = plugin_api
        self.hass_api = hass_api


class PluginApi():
    def __init__(self, react: ReactBase) -> None:
        self._react = react
        self.tasks: list[PluginTask] = []
        self.providers: dict[str, dict[str, Any]] = {}


    def register_plugin_task(self, task_type: type[PluginTask], **kwargs):
        task = task_type(self._react, **kwargs)
        self._react.task_manager.register_task(task)
        self.tasks.append(task)


    def register_plugin_provider(self, provider_type: str, provider_name: str, provider: Any):
        plugin_dict = self.providers.get(provider_type, None)
        if not plugin_dict:
            plugin_dict = {}
            self.providers[provider_type] = plugin_dict
        plugin_dict[provider_name] = provider


    def get_provider(self, provider_type: str, provider_name: str = None, entity_id: str = None) -> Any:
        result = None
        plugin_dict = self.providers.get(provider_type)
        if plugin_dict:
            if provider_name:
                result = plugin_dict.get(provider_name, None)
            if not result and entity_id:
                result = plugin_dict.get(entity_id, None)
        return result
    

    def unload_tasks(self):
        for task in self.tasks:
            self._react.task_manager.unload_task(task)
        self.tasks.clear()


class HassApi:
    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self.entity_registry = er.async_get(self.hass)


    async def async_hass_call_service(
        self,
        domain: str,
        service: str,
        service_data: dict[str, Any] | None = None,
        blocking: bool = False,
        context: Context | None = None,
        limit: float | None = SERVICE_CALL_LIMIT,
        target: dict[str, Any] | None = None,
    ) -> bool | None:
        return await self.hass.services.async_call(
            domain,
            service,
            service_data,
            blocking,
            context,
            limit,
            target,
        )
    

    def hass_get_state(self, entity_id: str) -> State | None:
        return self.hass.states.get(entity_id)
    

    def hass_get_data(self, key: str, default: Any = None) -> Any:
        return self.hass.data.get(key, default)
    

    def hass_set_data(self, key: str, data: Any) -> Any:
        self.hass.data[key] = data
        return data
    
    
    def hass_get_entity(self, entity_id: str) -> RegistryEntry | None:
        return self.entity_registry.async_get(entity_id) 
    

    def hass_service_available(self, domain: str, entity_id: str) -> bool:
        return self.hass.services.has_service(domain, entity_id)
    

    async def async_hass_wait(self, seconds: int):
        await sleep(seconds)


    def hass_get_uid_str(self) -> str:
        return uuid4().hex
    
    
    def hass_generate_media_source_id(self, message: str, engine: str | None = None, language: str | None = None, options: dict | None = None, cache: bool | None = None) -> str:
        return generate_media_source_id(self.hass, message, engine, language, options, cache)


class PluginFactory:
    def __init__(self, react: ReactBase) -> None:
        self._react = react
        self.plugin_api = PluginApi(react)
        self.hass_api = HassApi(react.hass)


    def load_plugins(self):
        for plugin in self._react.configuration.plugin_config.plugins:
            try:
                plugin_module = import_module(plugin.module)
                if hasattr(plugin_module, "load"):
                    plugin_module.load(plugin_api=self.plugin_api, hass_api=self.hass_api, config=plugin.config)
                else:
                    _LOGGER.error(f"PluginFactory - Invalid plugin configuration: load method missing in '{plugin_module}'")
            except:
                _LOGGER.exception(f"PluginFactory - Could not load plugin '{plugin.module}'")
        self._react.task_manager.execute_plugin_tasks()


    def reload(self):
        self.plugin_api.unload_tasks()
        self.load_plugins()
