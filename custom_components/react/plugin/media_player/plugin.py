import voluptuous as vol

from homeassistant.helpers import config_validation as cv

from custom_components.react.plugin.api import HassApi, PluginApi
from custom_components.react.plugin.factory import PluginBase
from custom_components.react.plugin.media_player.api import MediaPlayerApi, MediaPlayerConfig
from custom_components.react.plugin.media_player.const import (
    ATTR_MEDIA_PLAYER_PROVIDER, 
    ATTR_TTS_PROVIDER
)
from custom_components.react.plugin.media_player.tasks.speek_task import MediaPlayerSpeekTask
from custom_components.react.plugin.media_player.tasks.play_favorite_task import MediaPlayerPlayFavoriteTask
from custom_components.react.utils.logger import get_react_logger

_LOGGER = get_react_logger()

MEDIA_PLAYER_PLUGIN_CONFIG_SCHEMA = vol.Schema({
    vol.Optional(ATTR_MEDIA_PLAYER_PROVIDER) : cv.string,
    vol.Optional(ATTR_TTS_PROVIDER) : cv.string,
})


class Plugin(PluginBase):
    def __init__(self) -> None:
        super().__init__(MEDIA_PLAYER_PLUGIN_CONFIG_SCHEMA)


    def load(self, plugin_api: PluginApi, hass_api: HassApi, config: dict):
        _LOGGER.debug(f"Media-player plugin: Loading")

        api = MediaPlayerApi(plugin_api, hass_api, MediaPlayerConfig(config))
        
        plugin_api.register_plugin_task(MediaPlayerPlayFavoriteTask, api=api)
        plugin_api.register_plugin_task(MediaPlayerSpeekTask, api=api)