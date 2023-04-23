from homeassistant.components.media_player import (
    SERVICE_VOLUME_SET,
    SERVICE_PLAY_MEDIA,
)
from homeassistant.components.media_player.const import (
    DOMAIN as MEDIA_PLAYER_DOMAIN,
    ATTR_MEDIA_ANNOUNCE,
    ATTR_MEDIA_CONTENT_TYPE,
    ATTR_MEDIA_CONTENT_ID,
    ATTR_MEDIA_VOLUME_LEVEL,
    MediaType,
)
from homeassistant.const import (
    ATTR_ENTITY_ID
)
from homeassistant.core import Context

from custom_components.react.base import ReactBase
from custom_components.react.plugin.media_player.config import TtsConfig
from custom_components.react.plugin.media_player.const import TTS_DEFAULT_LANGUAGE
from custom_components.react.plugin.plugin_factory import HassApi, PluginApi
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
    def __init__(self, plugin_api: PluginApi, hass_api: HassApi, config: TtsConfig, engine: str) -> None:
        super().__init__(plugin_api, hass_api)
        
        self.config = config
        self.engine = engine

        
    async def async_speek(self, context: Context, entity_id: str, message: str, language: str, cache: bool, options: DynamicData):
        speek_data = {
            ATTR_ENTITY_ID: entity_id,
            ATTR_MEDIA_CONTENT_ID: self.hass_api.hass_generate_media_source_id(
                engine=self.engine,
                message=message,
                language=language or self.config.language or TTS_DEFAULT_LANGUAGE,
                options=options.as_dict() if options else self.config.options.as_dict() if self.config.options else {},
                cache=cache
            ),
            ATTR_MEDIA_CONTENT_TYPE: MediaType.MUSIC,
            ATTR_MEDIA_ANNOUNCE: True,
        }

        await self.hass_api.async_hass_call_service(
            MEDIA_PLAYER_DOMAIN,
            SERVICE_PLAY_MEDIA,
            speek_data,
            blocking=True,
            context=context,
        )