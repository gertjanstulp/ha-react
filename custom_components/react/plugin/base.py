from __future__ import annotations

from typing import Callable, Generic, TypeVar

from custom_components.react.plugin.hass_api import HassApi
from custom_components.react.tasks.plugin.base import BlockBase
from custom_components.react.utils.struct import DynamicData

T_config = TypeVar("T_config", bound=DynamicData)


class Plugin(Generic[T_config]):
    def __init__(self, hass_api: HassApi, config: T_config) -> None:
        super().__init__()

        self.hass_api = hass_api
        self.config = config

        self._api: PluginApiBase[T_config] = None
        self._providers: list[PluginProviderBase[T_config]] = []
        self._input_blocks: list[BlockBase] = []
        self._output_blocks: list[BlockBase] = []
    

    @property
    def api(self) -> PluginApiBase[T_config]:
        return self._api
    

    def _build(self, get_provider: Callable[[str, str], None]):
        self.get_provider = get_provider
        if self._api:
            self._api._build(self)
            self._api.load()
        for provider in self._providers:
            provider._build(self)
            provider.load()

        for block in self._input_blocks + self._output_blocks:
            block._build(self)
            block.load()
            block.start()


    def unload(self):
        for block in self._input_blocks:
            block.unload()
        for block in self._output_blocks:
            block.unload()
        self._input_blocks.clear()
        self._output_blocks.clear()


class PluginApiBase(Generic[T_config]):
    def __init__(self) -> None:
        self.plugin: Plugin[T_config] = None


    def _build(self, plugin: Plugin[T_config]):
        self.plugin = plugin


    def load(self):
        pass


T_api = TypeVar("T_api", bound=PluginApiBase)


class ApiType(Generic[T_api]):
    @property
    def api(self) -> T_api:
        return self.plugin.api


class PluginProviderBase(Generic[T_config]):
    def __init__(self) -> None:
        self.plugin: Plugin[T_config] = None


    def _build(self, plugin: Plugin[T_config]):
        self.plugin = plugin


    def load(self):
        pass
