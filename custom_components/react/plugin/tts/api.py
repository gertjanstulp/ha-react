from homeassistant.const import ATTR_ENTITY_ID, Platform
from homeassistant.core import Context

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


    async def async_media_player_speek(self, entity_id: str, message: str, language: str, options: dict, context: Context):
        self._debug(f"Speeking '{message}'")
        if not self.config.say_service:
            self.react.log.error("TtsPlugin - No say_service configured")
            return

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
            context)
