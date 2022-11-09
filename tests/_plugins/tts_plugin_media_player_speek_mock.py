from homeassistant.core import Context
from homeassistant.components.media_player.const import (
    ATTR_MEDIA_VOLUME_LEVEL
)
from homeassistant.const import (
    ATTR_ENTITY_ID, 
)

from custom_components.react.base import ReactBase
from custom_components.react.const import ATTR_EVENT_MESSAGE
from custom_components.react.utils.struct import DynamicData

from custom_components.react.plugin.plugin_factory import PluginApi
from custom_components.react.plugin.tts.tasks.media_player_speek import MediaPlayerSpeekTask
from custom_components.react.plugin.tts.const import (
    ATTR_EVENT_LANGUAGE, 
    ATTR_EVENT_OPTIONS, 
    ATTR_INTERRUPT_SERVICE, 
    ATTR_RESUME_SERVICE,
)

from tests.tst_context import TstContext


def load(plugin_api: PluginApi, config: DynamicData):
    plugin_api.register_default_task(MediaPlayerSpeekTaskMock)


class TtsApiMock():
    def __init__(self, react: ReactBase) -> None:
        self.react = react


    async def async_media_player_interrupt(self, context: Context, entity_id: str, interrupt_service: str):
        tc: TstContext = self.react.hass.data["test_context"]
        tc.register_plugin_data({
            ATTR_ENTITY_ID: entity_id,
            ATTR_INTERRUPT_SERVICE: interrupt_service,
        })


    async def async_media_player_set_volume(self, context: Context, entity_id: str, volume: float):
        tc: TstContext = self.react.hass.data["test_context"]
        tc.register_plugin_data({
            ATTR_ENTITY_ID: entity_id,
            ATTR_MEDIA_VOLUME_LEVEL: volume,
        })


    async def async_say(self, context: Context, entity_id: str, message: str, language: str, options: dict):
        tc: TstContext = self.react.hass.data["test_context"]
        tc.register_plugin_data({
            ATTR_ENTITY_ID: entity_id,
            ATTR_EVENT_MESSAGE: message,
            ATTR_EVENT_LANGUAGE: language,
            ATTR_EVENT_OPTIONS: options
        })


    async def async_media_player_resume(self, context: Context, entity_id: str, resume_service: str):
        tc: TstContext = self.react.hass.data["test_context"]
        if resume_service:
            tc.register_plugin_data({
                ATTR_ENTITY_ID: entity_id,
                ATTR_RESUME_SERVICE: resume_service,
            })


class MediaPlayerSpeekTaskMock(MediaPlayerSpeekTask):

    def __init__(self, react: ReactBase) -> None:
        api = TtsApiMock(react)
        super().__init__(react, api)