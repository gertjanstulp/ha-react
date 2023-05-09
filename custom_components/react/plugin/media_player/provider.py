from homeassistant.components.media_player import (
    SERVICE_VOLUME_SET
)
from homeassistant.components.media_player.const import (
    DOMAIN as MEDIA_PLAYER_DOMAIN,
    ATTR_MEDIA_VOLUME_LEVEL
)
from homeassistant.const import (
    ATTR_ENTITY_ID
)
from homeassistant.core import Context

from custom_components.react.base import ReactBase
from custom_components.react.plugin.api import HassApi, PluginApi
from custom_components.react.plugin.providers import PluginProvider
from custom_components.react.utils.struct import DynamicData


class MediaPlayerProvider(PluginProvider):
    def __init__(self, plugin_api: PluginApi, hass_api: HassApi) -> None:
        super().__init__(plugin_api, hass_api)


    @property
    def support_announce(self) -> bool:
        return False

    
    async def async_play_favorite(self, context: Context, entity_id: str, favorite_id: str):
        raise NotImplementedError()
    

    async def async_suspend(self, context: Context, entity_id: str):
        raise NotImplementedError()
    

    async def async_resume(self, context: Context, entity_id: str):
        raise NotImplementedError()
    

    async def async_set_volume(self, context: Context, entity_id: str, volume: float):
        data: dict = {
            ATTR_ENTITY_ID: entity_id,
            ATTR_MEDIA_VOLUME_LEVEL: volume
        }

        await self.hass_api.async_hass_call_service(
            MEDIA_PLAYER_DOMAIN,
            SERVICE_VOLUME_SET,
            data, 
            context
        )


class TtsProvider(PluginProvider):
    def __init__(self, plugin_api: PluginApi, hass_api: HassApi) -> None:
        super().__init__(plugin_api, hass_api)


    async def async_speek(self, context: Context, entity_id: str, message: str, language: str, cache: bool, options: DynamicData):
        raise NotImplementedError()