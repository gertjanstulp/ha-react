import voluptuous as vol

from homeassistant.helpers import config_validation as cv

from custom_components.react.plugin.const import PROVIDER_TYPE_UNIFI
from custom_components.react.plugin.factory import ApiSetupCallback, OutputBlockSetupCallback, PluginSetup, ProviderSetupCallback
from custom_components.react.plugin.unifi.api import UnifiApi
from custom_components.react.plugin.unifi.config import UnifiConfig
from custom_components.react.plugin.unifi.const import (
    ATTR_UNIFI_PROVIDER, 
    UNIFI_GENERIC_PROVIDER
)
from custom_components.react.plugin.unifi.output.reconnect_client_output_block import UnifiReconnectClientOutputBlock
from custom_components.react.plugin.unifi.provider import UnifiProvider


UNIFI_PLUGIN_CONFIG_SCHEMA = vol.Schema({
    vol.Optional(ATTR_UNIFI_PROVIDER) : cv.string,
})


class Setup(PluginSetup[UnifiConfig]):
    def __init__(self) -> None:
        super().__init__(UNIFI_PLUGIN_CONFIG_SCHEMA)


    def setup_config(self, raw_config: dict) -> UnifiConfig:
        return UnifiConfig(raw_config)
    

    def setup_api(self, setup: ApiSetupCallback):
        setup(UnifiApi)

    
    def setup_provider(self, setup: ProviderSetupCallback):
        setup(UnifiProvider, PROVIDER_TYPE_UNIFI, UNIFI_GENERIC_PROVIDER)


    def setup_output_blocks(self, setup: OutputBlockSetupCallback):
        setup(UnifiReconnectClientOutputBlock)
