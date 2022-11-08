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


def setup_plugin(plugin_api: PluginApi, config: DynamicData):
    plugin_api.register_default_task(MediaPlayerSpeekTaskMock)


class TtsApiMock():
    def __init__(self, react: ReactBase) -> None:
        self.react = react


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
        context: TstContext = self.react.hass.data["test_context"]
        
        if interrupt_service:
            context.register_plugin_data({
                ATTR_ENTITY_ID: entity_id,
                ATTR_INTERRUPT_SERVICE: interrupt_service,
            })

        if volume:
            context.register_plugin_data({
                ATTR_ENTITY_ID: entity_id,
                ATTR_MEDIA_VOLUME_LEVEL: volume,
            })

        context.register_plugin_data({
            ATTR_ENTITY_ID: entity_id,
            ATTR_EVENT_MESSAGE: message,
            ATTR_EVENT_LANGUAGE: language,
            ATTR_EVENT_OPTIONS: options
        })

        if resume_service:
            context.register_plugin_data({
                ATTR_ENTITY_ID: entity_id,
                ATTR_RESUME_SERVICE: resume_service,
            })


class MediaPlayerSpeekTaskMock(MediaPlayerSpeekTask):

    def __init__(self, react: ReactBase) -> None:
        api = TtsApiMock(react)
        super().__init__(react, api)