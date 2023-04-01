from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData

from custom_components.react.plugin.plugin_factory import PluginApi
from custom_components.react.plugin.media_player.api import MediaPlayerApi, MediaPlayerApiConfig
from custom_components.react.plugin.media_player.tasks.play_favorite_task import MediaPlayerPlayFavoriteTask

_LOGGER = get_react_logger()

def load(plugin_api: PluginApi, config: DynamicData):
    _LOGGER.debug(f"Media-player plugin: Loading")

    api = MediaPlayerApi(plugin_api, MediaPlayerApiConfig(config))
    plugin_api.register_plugin_task(MediaPlayerPlayFavoriteTask, api=api)