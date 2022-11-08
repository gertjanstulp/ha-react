from homeassistant.core import Context
from homeassistant.components.media_player.const import (
    ATTR_MEDIA_VOLUME_LEVEL
)
from homeassistant.const import (
    ATTR_ENTITY_ID, 
    SERVICE_VOLUME_SET,
    Platform,
)

from custom_components.react.base import ReactBase
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData
from custom_components.react.const import (
    ATTR_EVENT_MESSAGE,
)

from custom_components.react.plugin.tts.const import ATTR_EVENT_LANGUAGE, ATTR_EVENT_OPTIONS, TTS_DEFAULT_LANGUAGE

_LOGGER = get_react_logger()


class ApiConfig(DynamicData):
    def __init__(self, source: DynamicData = None) -> None:
        super().__init__()
        self.say_service: str = None
        self.language: str = None
        self.options: dict = None
        self.load(source)


class Api():
    def __init__(self, react: ReactBase, config: ApiConfig) -> None:
        self.react = react
        self.config = config


    def _debug(self, message: str):
        _LOGGER.debug(f"Tts plugin: Api - {message}")


    async def async_media_player_speek(self, 
        context: Context, 
        entity_id: str, 
        message: str, 
        language: str, 
        options: dict, 
        volume: float = None,
        interrupt_service: str = None, 
        resume_service: str = None, 
    ):
        self._debug(f"Speeking '{message}'")

        if not self.config.say_service:
            self.react.log.error("TtsPlugin - No say_service configured")
            return

        if interrupt_service:
            await self.async_media_player_interrupt(context, entity_id, interrupt_service)
        if volume:
            await self.async_media_player_set_volume(context, entity_id, volume)
        await self.async_say(context, entity_id, message, language, options)


    async def async_media_player_interrupt(self, context: Context, entity_id: str, interrupt_service: str):
        interrupt_data = {
            ATTR_ENTITY_ID: f"media_player.{entity_id}",
        }
        service_items = interrupt_service.split('.')
        await self.react.hass.services.async_call(
            service_items[0],
            service_items[1],
            interrupt_data,
            context,
        )


    async def async_media_player_set_volume(self, context: Context, entity_id: str, volume: float):
        volume_data = {
            ATTR_ENTITY_ID: f"media_player.{entity_id}",
            ATTR_MEDIA_VOLUME_LEVEL: volume,
        }
        await self.react.hass.services.async_call(
            Platform.MEDIA_PLAYER,
            SERVICE_VOLUME_SET,
            volume_data,
            context,
        )


    async def async_say(self, context: Context, entity_id: str, message: str, language: str, options: dict):
        speek_data = {
            ATTR_ENTITY_ID: f"media_player.{entity_id}",
            ATTR_EVENT_MESSAGE: message,
            ATTR_EVENT_LANGUAGE: language or self.config.language or TTS_DEFAULT_LANGUAGE,
            ATTR_EVENT_OPTIONS: options or self.config.options or {},
        }

        await self.react.hass.services.async_call(
            Platform.TTS, 
            self.config.say_service,
            speek_data,
            context,
        )
        
