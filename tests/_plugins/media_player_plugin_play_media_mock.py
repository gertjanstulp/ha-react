from homeassistant.core import Context
from homeassistant.const import (
    ATTR_ENTITY_ID, 
)
from homeassistant.components.media_player.const import (
    ATTR_MEDIA_CONTENT_TYPE,
    ATTR_MEDIA_CONTENT_ID,
)

from custom_components.react.base import ReactBase
from custom_components.react.plugin.media_player.tasks.play_media_task import MediaPlayerPlayMediaTask
from custom_components.react.plugin.plugin_factory import PluginApi
from custom_components.react.utils.struct import DynamicData
from tests.common import TEST_CONTEXT
from tests.tst_context import TstContext


def load(plugin_api: PluginApi, config: DynamicData):
    plugin_api.register_plugin_task(PlayMediaTaskMock)


class MediaPlayerApiMock():
    def __init__(self, react: ReactBase) -> None:
        self.react = react


    async def async_play_media(self, context: Context, entity_id: str, media_content_type: str, media_content_id: str):
        tc: TstContext = self.react.hass.data[TEST_CONTEXT]
        tc.register_plugin_data({
            ATTR_ENTITY_ID: entity_id,
            ATTR_MEDIA_CONTENT_TYPE: media_content_type,
            ATTR_MEDIA_CONTENT_ID: media_content_id
        })


class PlayMediaTaskMock(MediaPlayerPlayMediaTask):

    def __init__(self, react: ReactBase) -> None:
        api = MediaPlayerApiMock(react)
        super().__init__(react, api)