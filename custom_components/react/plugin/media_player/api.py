from homeassistant.core import Context

from custom_components.react.plugin.const import (
    PROVIDER_TYPE_MEDIA_PLAYER,
    PROVIDER_TYPE_TTS
)
from custom_components.react.plugin.media_player.config import MediaPlayerConfig
from custom_components.react.plugin.media_player.provider import MediaPlayerProvider, TtsProvider
from custom_components.react.plugin.api import ApiBase, HassApi, PluginApi
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData

_LOGGER = get_react_logger()


class MediaPlayerApi(ApiBase):
    def __init__(self, plugin_api: PluginApi, hass_api: HassApi, config: MediaPlayerConfig) -> None:
        super().__init__(plugin_api, hass_api)
        self.config = config


    def _debug(self, message: str):
        _LOGGER.debug(f"Mediaplayer plugin: Api - {message}")

    
    async def async_play_favorite(self, 
        context: Context,
        entity_id: str,
        favorite_id: str,
        media_player_provider: str, 
    ):
        self._debug(f"Playing favorite '{favorite_id}' on '{entity_id}'")
        try:
            full_entity_id = f"media_player.{entity_id}"
            if state := self.hass_api.hass_get_state(full_entity_id):
                value = state.state
            else:
                _LOGGER.warn(f"Mediaplayer plugin: Api - {full_entity_id} not found")
                return
            
            provider = self.get_media_player_provider(full_entity_id, media_player_provider)
            if provider:
                await provider.async_play_favorite(context, entity_id, favorite_id)
        except:
            _LOGGER.exception("Mediaplayer plugin: Api - Playing media failed")


    async def async_speek(self, 
        context: Context, 
        entity_id: str, 
        announce: bool, 
        message: str, 
        language: str, 
        volume: float,
        wait: int,
        cache: bool,
        options: DynamicData,
        media_player_provider: str,
        tts_provider: str,
    ):
        self._debug(f"Speeking '{message}' on mediaplayer")
        try:
            full_entity_id = f"media_player.{entity_id}"
            if state := self.hass_api.hass_get_state(full_entity_id):
                value = state.state
            else:
                _LOGGER.warn(f"Mediaplayer plugin: Api - {full_entity_id} not found")
                return
            
            # Retrieve providers
            mp_provider = self.get_media_player_provider(full_entity_id, media_player_provider)
            if not mp_provider: return
            t_provider = self.get_tts_provider(tts_provider)
            if not t_provider: return

            # If the mediaplayer doesn't support 'announce' it has to be suspended before sending tts messages
            if announce and not mp_provider.support_announce:
                await mp_provider.async_suspend(context, full_entity_id)
            
            if volume:
                await mp_provider.async_set_volume(context, full_entity_id, volume)

            await t_provider.async_speek(context, full_entity_id, message, language, cache, options)

            if wait:
                await self.hass_api.async_hass_wait(wait)

            # If the mediaplayer doesn't support 'announce' it has to be resumed after sending tts messages
            if announce and not mp_provider.support_announce:
                await mp_provider.async_resume(context, full_entity_id)
        except:
            _LOGGER.exception("Speeking message failed")


    def get_tts_provider(self, tts_provider: str) -> TtsProvider:
        tts_provider = tts_provider or self.config.tts_provider
        result = self.plugin_api.get_provider(PROVIDER_TYPE_TTS, tts_provider)
        if not result:
            _LOGGER.error(f"Mediaplayer plugin: Api - Tts provider for '{tts_provider}' not found")
            return None
        return result
        
    def get_media_player_provider(self, entity_id: str, media_player_provider: str) -> MediaPlayerProvider:
        result = None
    
        entity = self.hass_api.hass_get_entity(entity_id)
        if entity:
            result = self.plugin_api.get_provider(PROVIDER_TYPE_MEDIA_PLAYER, entity.platform)
        
        if not result:
            media_player_provider = media_player_provider or self.config.media_player_provider
            if media_player_provider:
                result = self.plugin_api.get_provider(PROVIDER_TYPE_MEDIA_PLAYER, media_player_provider)
    
        if not result:
            target = entity_id
            if media_player_provider:
                target = f"{target}/{media_player_provider}"
            _LOGGER.error(f"Mediaplayer plugin: Api - Mediaplayer provider for '{target}' not found")
            return None
        return result
