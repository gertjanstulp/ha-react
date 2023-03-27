from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData

from custom_components.react.plugin.plugin_factory import PluginApi
from custom_components.react.plugin.tts.api import TtsApi, TtsApiConfig
from custom_components.react.plugin.tts.tasks.media_player_speek_task import MediaPlayerSpeekTask

_LOGGER = get_react_logger()

def load(plugin_api: PluginApi, config: DynamicData):
    _LOGGER.debug(f"Tts plugin: Loading")

    api = TtsApi(plugin_api.react, TtsApiConfig(config))
    plugin_api.register_plugin_task(MediaPlayerSpeekTask, api=api)