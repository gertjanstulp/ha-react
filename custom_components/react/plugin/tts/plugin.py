from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData

from custom_components.react.plugin.plugin_factory import PluginApi
from custom_components.react.plugin.tts.api import Api, ApiConfig
from custom_components.react.plugin.tts.tasks.media_player_speek import MediaPlayerSpeekTask


def setup_plugin(plugin_api: PluginApi, config: DynamicData):
    get_react_logger().debug(f"Tts plugin: Setting up")

    api = Api(plugin_api.react, ApiConfig(config))
    plugin_api.register_default_task(MediaPlayerSpeekTask, api=api)
