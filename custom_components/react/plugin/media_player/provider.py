from typing import Generic, TypeVar

from homeassistant.components.media_player import SERVICE_VOLUME_SET
from homeassistant.components.media_player.const import (
    DOMAIN as MEDIA_PLAYER_DOMAIN,
    ATTR_MEDIA_VOLUME_LEVEL
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import Context

from custom_components.react.plugin.base import PluginProviderBase
from custom_components.react.utils.struct import DynamicData

T_config = TypeVar("T_config", bound=DynamicData)


class MediaPlayerProvider(Generic[T_config], PluginProviderBase[T_config]):

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

        await self.plugin.hass_api.async_hass_call_service(
            MEDIA_PLAYER_DOMAIN,
            SERVICE_VOLUME_SET,
            data, 
            context
        )



class TtsProvider(Generic[T_config], PluginProviderBase[T_config]):

    async def async_speek(self, context: Context, entity_id: str, message: str, language: str, cache: bool, options: DynamicData):
        raise NotImplementedError()