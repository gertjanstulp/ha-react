from homeassistant.core import Context
from homeassistant.const import (
    ATTR_ENTITY_ID, 
)

from custom_components.react.base import ReactBase
from custom_components.react.plugin.const import SERVICE_TYPE_DEFAULT
from custom_components.react.plugin.media_player.api import MediaPlayerApi, MediaPlayerApiConfig
from custom_components.react.plugin.media_player.const import ATTR_FAVORITE_ID, PLUGIN_NAME
from custom_components.react.plugin.media_player.service import MediaPlayerService
from custom_components.react.plugin.media_player.tasks.play_favorite_task import MediaPlayerPlayFavoriteTask
from custom_components.react.plugin.plugin_factory import PluginApi
from custom_components.react.utils.struct import DynamicData
from tests.common import TEST_CONTEXT
from tests.tst_context import TstContext


def load(plugin_api: PluginApi, config: DynamicData):
    api = MediaPlayerApi(plugin_api, MediaPlayerApiConfig(config))
    plugin_api.register_plugin_task(MediaPlayerPlayFavoriteTask, api=api)
    plugin_api.register_plugin_service(PLUGIN_NAME, SERVICE_TYPE_DEFAULT, MediaPlayerServiceMock(plugin_api.react))


class MediaPlayerServiceMock(MediaPlayerService):
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react)


    async def async_play_favorite(self, context: Context, entity_id: str, favorite_id: str):
        tc: TstContext = self.react.hass.data[TEST_CONTEXT]
        tc.register_plugin_data({
            ATTR_ENTITY_ID: entity_id,
            ATTR_FAVORITE_ID: favorite_id,
        })
