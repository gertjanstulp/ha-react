

from homeassistant.core import Context
from homeassistant.const import (
    ATTR_ENTITY_ID, 
)

from custom_components.react.base import ReactBase
from custom_components.react.const import ATTR_ENTITY, ATTR_EVENT_MESSAGE, ATTR_LANGUAGE, ATTR_OPTIONS
from custom_components.react.plugin.plugin_factory import PluginApi
from custom_components.react.plugin.telegram.const import ATTR_MESSAGE_DATA
from custom_components.react.plugin.telegram.tasks.notify_send_message_task import NotifySendMessageTask
from custom_components.react.plugin.tts.tasks.media_player_speek import MediaPlayerSpeekTask
from custom_components.react.utils.struct import DynamicData
from tests.tst_context import TstContext


def setup_plugin(plugin_api: PluginApi, config: DynamicData):
    plugin_api.register_default_task(MediaPlayerSpeekTaskMock)


class TtsApiMock():
    def __init__(self, react: ReactBase) -> None:
        self.react = react


    async def async_media_player_speek(self, entity_id: str, message: str, language: str, options: dict, context: Context):
        context: TstContext = self.react.hass.data["test_context"]
        context.register_plugin_data({
            ATTR_ENTITY_ID: entity_id,
            ATTR_EVENT_MESSAGE: message,
            ATTR_LANGUAGE: language,
            ATTR_OPTIONS: options
        })


class MediaPlayerSpeekTaskMock(MediaPlayerSpeekTask):

    def __init__(self, react: ReactBase) -> None:
        api = TtsApiMock(react)
        super().__init__(react, api)