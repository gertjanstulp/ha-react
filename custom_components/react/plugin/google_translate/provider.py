from homeassistant.components.media_player.const import (
    ATTR_MEDIA_ANNOUNCE,
    ATTR_MEDIA_CONTENT_TYPE,
    ATTR_MEDIA_CONTENT_ID,
    DOMAIN as MEDIA_PLAYER_DOMAIN,
    SERVICE_PLAY_MEDIA,
    MediaType,
)
from homeassistant.const import (
    ATTR_ENTITY_ID,
)
from homeassistant.core import Context

from custom_components.react.plugin.google_translate.config import GoogleTranslateConfig
from custom_components.react.plugin.google_translate.const import TTS_GOOGLE_TRANSLATE_PROVIDER
from custom_components.react.plugin.media_player.const import TTS_DEFAULT_LANGUAGE
from custom_components.react.plugin.media_player.provider import TtsProvider
from custom_components.react.utils.struct import DynamicData


class GoogleTranslateTtsProvider(TtsProvider[GoogleTranslateConfig]):
        
    async def async_speek(self, context: Context, entity_id: str, message: str, language: str, cache: bool, options: DynamicData):
        speek_data = {
            ATTR_ENTITY_ID: entity_id,
            ATTR_MEDIA_CONTENT_ID: self.plugin.hass_api.hass_generate_media_source_id(
                engine=TTS_GOOGLE_TRANSLATE_PROVIDER,
                message=message,
                language=language or self.plugin.config.language or TTS_DEFAULT_LANGUAGE,
                options=options.as_dict() if options else self.plugin.config.options.as_dict() if self.plugin.config.options else {},
                cache=cache
            ),
            ATTR_MEDIA_CONTENT_TYPE: MediaType.MUSIC,
            ATTR_MEDIA_ANNOUNCE: True,
        }

        await self.plugin.hass_api.async_hass_call_service(
            MEDIA_PLAYER_DOMAIN,
            SERVICE_PLAY_MEDIA,
            speek_data,
            blocking=True,
            context=context,
        )
