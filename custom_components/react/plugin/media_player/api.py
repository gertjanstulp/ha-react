from homeassistant.core import Context

from custom_components.react.plugin.const import (
    PROVIDER_TYPE_MEDIA_PLAYER,
    PROVIDER_TYPE_TTS
)
from custom_components.react.plugin.media_player.config import MediaPlayerConfig
from custom_components.react.plugin.media_player.provider import MediaPlayerProvider, TtsProvider
from custom_components.react.plugin.base import PluginApiBase
from custom_components.react.utils.session import Session
from custom_components.react.utils.struct import DynamicData


class MediaPlayerApi(PluginApiBase[MediaPlayerConfig]):

    async def async_play_favorite(self, 
        session: Session,
        context: Context,
        entity_id: str,
        favorite_id: str,
        media_player_provider: str, 
    ):
        session.debug(self.logger, f"Playing favorite '{favorite_id}' on '{entity_id}'")
        try:
            full_entity_id = f"media_player.{entity_id}"
            if state := self.plugin.hass_api.hass_get_state(full_entity_id):
                value = state.state
            else:
                session.warning(self.plugin.logger, f"{full_entity_id} not found")
                return
            
            provider = self.get_media_player_provider(session, full_entity_id, media_player_provider)
            if provider:
                await provider.async_play_favorite(session, context, entity_id, favorite_id)
        except:
            session.exception("Playing media failed")


    async def async_pause(self,
        session: Session,
        context: Context, 
        entity_id: str, 
        media_player_provider: str,
    ):
        session.debug(self.logger, f"Pausing mediaplayer")
        try:
            full_entity_id = f"media_player.{entity_id}"
            if state := self.plugin.hass_api.hass_get_state(full_entity_id):
                value = state.state
            else:
                session.warning(self.plugin.logger, f"{full_entity_id} not found")
                return
            
            provider = self.get_media_player_provider(session, full_entity_id, media_player_provider)
            if provider:
                await provider.async_pause(session, context, entity_id)
        except:
            session.exception("Pausing failed")


    async def async_speek(self, 
        session: Session,
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
        session.debug(self.logger, f"Speeking '{message}' on mediaplayer")
        try:
            full_entity_id = f"media_player.{entity_id}"
            if state := self.plugin.hass_api.hass_get_state(full_entity_id):
                value = state.state
            else:
                session.warning(self.plugin.logger, f"{full_entity_id} not found")
                return
            
            # Retrieve providers
            mp_provider = self.get_media_player_provider(session, full_entity_id, media_player_provider)
            if not mp_provider: return
            t_provider = self.get_tts_provider(session, tts_provider)
            if not t_provider: return

            # If the mediaplayer doesn't support 'announce' it has to be suspended before sending tts messages
            if announce and not mp_provider.support_announce:
                await mp_provider.async_suspend(session, context, full_entity_id)
            
            if volume:
                await mp_provider.async_set_volume(session, context, full_entity_id, volume)

            await t_provider.async_speek(session, context, full_entity_id, message, language, cache, options)

            if wait:
                await self.plugin.hass_api.async_hass_wait(wait)

            # If the mediaplayer doesn't support 'announce' it has to be resumed after sending tts messages
            if announce and not mp_provider.support_announce:
                await mp_provider.async_resume(session, context, full_entity_id)
        except:
            session.exception("Speeking message failed")


    def get_tts_provider(self, session: Session, tts_provider: str) -> TtsProvider:
        tts_provider = tts_provider or self.plugin.config.tts_provider
        result = self.plugin.get_provider(PROVIDER_TYPE_TTS, tts_provider)
        if not result:
            if tts_provider:
                session.error(self.plugin.logger, f"Tts provider for '{tts_provider}' not found")
            else:
                session.error(self.plugin.logger, f"Tts provider not provided")
            return None
        return result
    
        
    def get_media_player_provider(self, session: Session, entity_id: str, media_player_provider: str) -> MediaPlayerProvider:
        result = None
    
        entity = self.plugin.hass_api.hass_get_entity(entity_id)
        if entity:
            result = self.plugin.get_provider(PROVIDER_TYPE_MEDIA_PLAYER, entity.platform)
        
        if not result:
            media_player_provider = media_player_provider or self.plugin.config.media_player_provider
            if media_player_provider:
                result = self.plugin.get_provider(PROVIDER_TYPE_MEDIA_PLAYER, media_player_provider)
    
        if not result:
            target = entity_id
            if media_player_provider:
                target = f"{target}/{media_player_provider}"
            session.error(self.plugin.logger, f"Mediaplayer provider for '{target}' not found")
            return None
        return result
