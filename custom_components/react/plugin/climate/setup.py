import voluptuous as vol

from homeassistant.helpers import config_validation as cv
from custom_components.react.plugin.climate.output.set_temperature_output_block import ClimateSetTemperatureOutputBlock
from custom_components.react.plugin.climate.provider import ClimateProvider
from custom_components.react.plugin.const import PROVIDER_TYPE_CLIMATE

from custom_components.react.plugin.factory import ApiSetupCallback, OutputBlockSetupCallback, PluginSetup, ProviderSetupCallback
from custom_components.react.plugin.climate.api import ClimateApi, ClimateConfig
from custom_components.react.plugin.climate.config import ClimateConfig
from custom_components.react.plugin.climate.const import (
    ATTR_CLIMATE_PROVIDER,
    CLIMATE_GENERIC_PROVIDER, 
)


CLIMATE_PLUGIN_CONFIG_SCHEMA = vol.Schema({
    vol.Optional(ATTR_CLIMATE_PROVIDER) : cv.string,
})


class Setup(PluginSetup[ClimateConfig]):
    def __init__(self) -> None:
        super().__init__(CLIMATE_PLUGIN_CONFIG_SCHEMA)


    def setup_config(self, raw_config: dict) -> ClimateConfig:
        return ClimateConfig(raw_config)


    def setup_api(self, setup: ApiSetupCallback):
        setup(ClimateApi)


    def setup_provider(self, setup: ProviderSetupCallback):
        setup(ClimateProvider[ClimateConfig], PROVIDER_TYPE_CLIMATE, CLIMATE_GENERIC_PROVIDER)
        
    
    def setup_output_blocks(self, setup: OutputBlockSetupCallback):
        setup(
            [
                ClimateSetTemperatureOutputBlock,
            ],
        )
