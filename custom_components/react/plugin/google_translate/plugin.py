import voluptuous as vol

from homeassistant.components.tts import (
    ATTR_OPTIONS,
    ATTR_LANGUAGE,
)
from homeassistant.helpers import config_validation as cv

from custom_components.react.plugin.const import PROVIDER_TYPE_TTS
from custom_components.react.plugin.factory import PluginBase
from custom_components.react.plugin.google_translate.config import GoogleTranslateConfig
from custom_components.react.plugin.google_translate.const import (
    ATTR_TTS_TLD, 
    TTS_GOOGLE_TRANSLATE_PROVIDER
)
from custom_components.react.plugin.google_translate.provider import GoogleTranslateTtsProvider
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData

from custom_components.react.plugin.api import HassApi, PluginApi

_LOGGER = get_react_logger()

GOOGLE_TRANSLATE_PLUGIN_SCHEMA = vol.Schema({
    vol.Optional(ATTR_LANGUAGE) : cv.string,
    vol.Optional(ATTR_OPTIONS) : vol.Schema({
        vol.Optional(ATTR_TTS_TLD) : cv.string
    })
})


class Plugin(PluginBase):
    def __init__(self) -> None:
        super().__init__(GOOGLE_TRANSLATE_PLUGIN_SCHEMA)


    def load(self, plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
        _LOGGER.debug(f"Google-translate plugin: Loading")
        
        plugin_api.register_plugin_provider(
            PROVIDER_TYPE_TTS, 
            TTS_GOOGLE_TRANSLATE_PROVIDER, 
            GoogleTranslateTtsProvider(plugin_api, hass_api, GoogleTranslateConfig(config or {}))
        )
