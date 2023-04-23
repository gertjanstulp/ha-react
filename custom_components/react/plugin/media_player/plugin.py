from custom_components.react.plugin.media_player.tasks.speek_task import MediaPlayerSpeekTask
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData

from custom_components.react.plugin.plugin_factory import HassApi, PluginApi
from custom_components.react.plugin.media_player.api import MediaPlayerApi, MediaPlayerConfig
from custom_components.react.plugin.media_player.tasks.play_favorite_task import MediaPlayerPlayFavoriteTask

_LOGGER = get_react_logger()

def load(plugin_api: PluginApi, hass_api: HassApi, config: dict):
    loader = MediaPlayerPluginLoader()
    loader.load(plugin_api, hass_api, config)


class MediaPlayerPluginLoader:
    def load(self, plugin_api: PluginApi, hass_api: HassApi, config: dict):
        _LOGGER.debug(f"Media-player plugin: Loading")

        api = MediaPlayerApi(plugin_api, hass_api, MediaPlayerConfig(config))
        
        plugin_api.register_plugin_task(MediaPlayerPlayFavoriteTask, api=api)
        plugin_api.register_plugin_task(MediaPlayerSpeekTask, api=api)