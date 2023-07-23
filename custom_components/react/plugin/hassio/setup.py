import voluptuous as vol

from homeassistant.helpers import config_validation as cv

from custom_components.react.plugin.const import PROVIDER_TYPE_HASSIO
from custom_components.react.plugin.factory import ApiSetupCallback, OutputBlockSetupCallback, PluginSetup, ProviderSetupCallback
from custom_components.react.plugin.hassio.api import HassioApi
from custom_components.react.plugin.hassio.config import HassioConfig
from custom_components.react.plugin.hassio.const import (
    ATTR_HASSIO_PROVIDER, 
    HASSIO_GENERIC_PROVIDER
)
from custom_components.react.plugin.hassio.output.restart_addon_output_block import HassioRestartAddonOutputBlock
from custom_components.react.plugin.hassio.provider import HassioProvider


HASSIO_PLUGIN_CONFIG_SCHEMA = vol.Schema({
    vol.Optional(ATTR_HASSIO_PROVIDER) : cv.string,
})


class Setup(PluginSetup[HassioConfig]):
    def __init__(self) -> None:
        super().__init__(HASSIO_PLUGIN_CONFIG_SCHEMA)


    def setup_config(self, raw_config: dict) -> HassioConfig:
        return HassioConfig(raw_config)
    

    def setup_api(self, setup: ApiSetupCallback):
        setup(HassioApi)

    
    def setup_provider(self, setup: ProviderSetupCallback):
        setup(HassioProvider, PROVIDER_TYPE_HASSIO, HASSIO_GENERIC_PROVIDER)


    def setup_output_blocks(self, setup: OutputBlockSetupCallback):
        setup(HassioRestartAddonOutputBlock)
