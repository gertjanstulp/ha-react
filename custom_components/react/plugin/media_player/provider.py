from typing import Generic, TypeVar

from homeassistant.components.media_player import (
    SERVICE_MEDIA_PAUSE,
    SERVICE_VOLUME_SET, 
)
from homeassistant.components.media_player.const import (
    DOMAIN as MEDIA_PLAYER_DOMAIN,
    ATTR_MEDIA_VOLUME_LEVEL
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import Context

from custom_components.react.plugin.base import PluginProviderBase
from custom_components.react.utils.session import Session
from custom_components.react.utils.struct import DynamicData

T_config = TypeVar("T_config", bound=DynamicData)


class MediaPlayerProvider(Generic[T_config], PluginProviderBase[T_config]):

    @property
    def support_announce(self) -> bool:
        return False

    
    async def async_play_favorite(self, session: Session, context: Context, entity_id: str, favorite_id: str):
        raise NotImplementedError()
    

    async def async_play_album(self, session: Session, context: Context, entity_id: str, album_id: str):
        raise NotImplementedError()


    async def async_play_playlist(self, session: Session, context: Context, entity_id: str, playlist_id: str):
        raise NotImplementedError()


    async def async_pause(self, session: Session, context: Context, entity_id: str):
        data: dict = {
            ATTR_ENTITY_ID: entity_id,
        }

        await self.plugin.hass_api.async_hass_call_service(
            MEDIA_PLAYER_DOMAIN,
            SERVICE_MEDIA_PAUSE,
            service_data=data, 
            context=context,
        )
    

    async def async_suspend(self, session: Session, context: Context, entity_id: str):
        raise NotImplementedError()
    

    async def async_resume(self, session: Session, context: Context, entity_id: str):
        raise NotImplementedError()
    

    async def async_set_volume(self, session: Session, context: Context, entity_id: str, volume: float):
        data: dict = {
            ATTR_ENTITY_ID: entity_id,
            ATTR_MEDIA_VOLUME_LEVEL: volume
        }

        await self.plugin.hass_api.async_hass_call_service(
            MEDIA_PLAYER_DOMAIN,
            SERVICE_VOLUME_SET,
            service_data=data, 
            context=context,
        )



class TtsProvider(Generic[T_config], PluginProviderBase[T_config]):

    async def async_speak(self, session: Session, context: Context, entity_id: str, message: str, language: str, cache: bool, options: DynamicData):
        raise NotImplementedError()