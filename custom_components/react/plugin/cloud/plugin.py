from custom_components.react.plugin.const import PROVIDER_TYPE_TTS
from custom_components.react.plugin.cloud.const import TTS_CLOUD_PROVIDER
from custom_components.react.plugin.cloud.provider import CloudTtsProvider
from custom_components.react.plugin.media_player.config import TtsConfig
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData

from custom_components.react.plugin.plugin_factory import HassApi, PluginApi

_LOGGER = get_react_logger()

def load(plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
    loader = CloudPluginLoader()
    loader.load(plugin_api, hass_api, config)


class CloudPluginLoader:
    def load(self, plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
        _LOGGER.debug(f"Cloud plugin: Loading")
        
        plugin_api.register_plugin_provider(
            PROVIDER_TYPE_TTS, 
            TTS_CLOUD_PROVIDER, 
            CloudTtsProvider(plugin_api, hass_api, TtsConfig(config or {}))
        )
