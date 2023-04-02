from custom_components.react.plugin.const import PROVIDER_TYPE_TTS
from custom_components.react.plugin.google_translate.config import GoogleTranslateConfig
from custom_components.react.plugin.google_translate.const import TTS_GOOGLE_TRANSLATE_PROVIDER
from custom_components.react.plugin.google_translate.provider import GoogleTranslateTtsProvider
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData

from custom_components.react.plugin.plugin_factory import HassApi, PluginApi

_LOGGER = get_react_logger()

def load(plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
    loader = GoogleTranslatePluginLoader()
    loader.load(plugin_api, hass_api, config)


class GoogleTranslatePluginLoader:
    def load(self, plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
        _LOGGER.debug(f"Google-translate plugin: Loading")
        
        plugin_api.register_plugin_provider(
            PROVIDER_TYPE_TTS, 
            TTS_GOOGLE_TRANSLATE_PROVIDER, 
            GoogleTranslateTtsProvider(plugin_api, hass_api, GoogleTranslateConfig(config or {}))
        )
