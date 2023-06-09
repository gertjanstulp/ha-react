import voluptuous as vol

from homeassistant.components.tts import (
    ATTR_OPTIONS,
    ATTR_LANGUAGE,
)
from homeassistant.helpers import config_validation as cv

from custom_components.react.plugin.const import PROVIDER_TYPE_TTS
from custom_components.react.plugin.factory import PluginSetup, ProviderSetupCallback
from custom_components.react.plugin.google_translate.config import GoogleTranslateConfig
from custom_components.react.plugin.google_translate.const import (
    ATTR_TTS_TLD, 
    TTS_GOOGLE_TRANSLATE_PROVIDER
)
from custom_components.react.plugin.google_translate.provider import GoogleTranslateTtsProvider


GOOGLE_TRANSLATE_PLUGIN_SCHEMA = vol.Schema({
    vol.Optional(ATTR_LANGUAGE) : cv.string,
    vol.Optional(ATTR_OPTIONS) : vol.Schema({
        vol.Optional(ATTR_TTS_TLD) : cv.string
    })
})


class Setup(PluginSetup[GoogleTranslateConfig]):
    def __init__(self) -> None:
        super().__init__(GOOGLE_TRANSLATE_PLUGIN_SCHEMA)


    def setup_config(self, raw_config: dict) -> GoogleTranslateConfig:
        return GoogleTranslateConfig(raw_config)


    def setup_provider(self, setup: ProviderSetupCallback):
        setup(GoogleTranslateTtsProvider, PROVIDER_TYPE_TTS, TTS_GOOGLE_TRANSLATE_PROVIDER)
