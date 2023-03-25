from asyncio import sleep
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


class TtsApiConfig(DynamicData):
    def __init__(self, source: DynamicData = None) -> None:
        super().__init__()
        self.say_service: str = None
        self.language: str = None
        self.options: DynamicData = None
        self.load(source)


class TtsApi():
    def __init__(self, react: ReactBase, config: TtsApiConfig) -> None:
        self.react = react
        self.config = config


    def _debug(self, message: str):
        _LOGGER.debug(f"Tts plugin: Api - {message}")


    def verify_config(self) -> bool:
        if not self.config.say_service:
            _LOGGER.error("TtsPlugin - No say_service configured")
            return False
        return True


    async def async_media_player_interrupt(self, context: Context, entity_id: str, interrupt_service: str):
        self._debug(f"Interrupting mediaplayer with '{interrupt_service}'")
        try:
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
        except:
            _LOGGER.exception("Interrupting mediaplayer failed")


    async def async_media_player_set_volume(self, context: Context, entity_id: str, volume: float):
        self._debug(f"Setting mediaplayer volume to '{str(volume)}'")
        try:
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
        except:
            _LOGGER.exception("Setting mediaplayer volume failed")


    async def async_say(self, context: Context, entity_id: str, message: str, language: str, options: DynamicData):
        self._debug(f"Saying '{message}' on mediaplayer")
        try:
            speek_data = {
                ATTR_ENTITY_ID: f"media_player.{entity_id}",
                ATTR_EVENT_MESSAGE: message,
                ATTR_EVENT_LANGUAGE: language or self.config.language or TTS_DEFAULT_LANGUAGE,
                ATTR_EVENT_OPTIONS: options.as_dict() if options else self.config.options.as_dict() if self.config.options else {},
            }

            await self.react.hass.services.async_call(
                Platform.TTS, 
                self.config.say_service,
                speek_data,
                context,
            )
        except:
            _LOGGER.exception("Saying message failed")


    async def async_wait(self, wait: int):
        self._debug(f"Waiting '{wait}' seconds before continuing")
        await sleep(wait)


    async def async_media_player_resume(self, context: Context, entity_id: str, resume_service: str):
        self._debug(f"Resuming mediaplayer with '{resume_service}'")
        try:
            interrupt_data = {
                ATTR_ENTITY_ID: f"media_player.{entity_id}",
            }
            service_items = resume_service.split('.')
            await self.react.hass.services.async_call(
                service_items[0],
                service_items[1],
                interrupt_data,
                context,
            )
        except:
            _LOGGER.exception("Resuming mediaplayer failed")
        
