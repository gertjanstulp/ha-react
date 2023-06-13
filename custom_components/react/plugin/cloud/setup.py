import voluptuous as vol

from homeassistant.components.tts import (
    ATTR_LANGUAGE,
    ATTR_OPTIONS,
    ATTR_VOICE,
)
from homeassistant.helpers import config_validation as cv

from custom_components.react.plugin.cloud.config import CloudConfig
from custom_components.react.plugin.const import PROVIDER_TYPE_TTS
from custom_components.react.plugin.cloud.const import TTS_CLOUD_PROVIDER
from custom_components.react.plugin.cloud.provider import CloudTtsProvider
from custom_components.react.plugin.factory import PluginSetup, ProviderSetupCallback


CLOUD_PLUGIN_SCHEMA = vol.Schema({
    vol.Optional(ATTR_LANGUAGE) : cv.string,
    vol.Optional(ATTR_OPTIONS) : vol.Schema({
        vol.Optional(ATTR_VOICE): cv.string,
    })
})

class Setup(PluginSetup[CloudConfig]):
    def __init__(self) -> None:
        super().__init__(CLOUD_PLUGIN_SCHEMA)


    def setup_config(self, raw_config: dict) -> CloudConfig:
        return CloudConfig(raw_config)


    def setup_provider(self, setup: ProviderSetupCallback):
        setup(CloudTtsProvider, PROVIDER_TYPE_TTS, TTS_CLOUD_PROVIDER)
