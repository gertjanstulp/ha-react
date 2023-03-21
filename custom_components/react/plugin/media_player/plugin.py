from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData

from custom_components.react.plugin.plugin_factory import PluginApi
from custom_components.react.plugin.media_player.api import Api, ApiConfig
from custom_components.react.plugin.media_player.tasks.play_media_task import MediaPlayerPlayMediaTask

_LOGGER = get_react_logger()

def load(plugin_api: PluginApi, config: DynamicData):
    _LOGGER.debug(f"Media-player plugin: Loading")

    api = Api(plugin_api.react, ApiConfig(config))
    plugin_api.register_plugin_task(MediaPlayerPlayMediaTask, api=api)