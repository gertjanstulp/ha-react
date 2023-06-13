import voluptuous as vol

from homeassistant.helpers import config_validation as cv

from custom_components.react.plugin.const import PROVIDER_TYPE_FAN
from custom_components.react.plugin.factory import ApiSetupCallback, InputBlockSetupCallback, OutputBlockSetupCallback, PluginSetup, ProviderSetupCallback
from custom_components.react.plugin.fan.api import FanApi
from custom_components.react.plugin.fan.config import FanConfig
from custom_components.react.plugin.fan.const import (
    ATTR_FAN_OFF_PERCENTAGE,
    ATTR_FAN_ON_PERCENTAGE,
    ATTR_FAN_PROVIDER, 
    FAN_GENERIC_PROVIDER
)
from custom_components.react.plugin.fan.output.decrease_speed_output_block import FanDecreaseSpeedOutputBlock
from custom_components.react.plugin.fan.output.increase_speed_output_block import FanIncreaseSpeedOutputBlock
from custom_components.react.plugin.fan.output.set_percentage_output_block import FanSetPercentageOutputBlock
from custom_components.react.plugin.fan.provider import FanProvider
from custom_components.react.plugin.fan.input.state_change_input_block import FanStateChangeInputBlock


FAN_PLUGIN_CONFIG_SCHEMA = vol.Schema({
    vol.Optional(ATTR_FAN_PROVIDER) : cv.string,
    vol.Optional(ATTR_FAN_ON_PERCENTAGE) : vol.Coerce(int),
    vol.Optional(ATTR_FAN_OFF_PERCENTAGE) : vol.Coerce(int),
})


class Setup(PluginSetup[FanConfig]):
    def __init__(self) -> None:
        super().__init__(FAN_PLUGIN_CONFIG_SCHEMA)


    def setup_config(self, raw_config: dict) -> FanConfig:
        return FanConfig(raw_config)
    

    def setup_api(self, setup: ApiSetupCallback):
        setup(FanApi)


    def setup_provider(self, setup: ProviderSetupCallback):
        setup(FanProvider, PROVIDER_TYPE_FAN, FAN_GENERIC_PROVIDER)
    

    def setup_input_blocks(self, setup: InputBlockSetupCallback):
        setup(FanStateChangeInputBlock)


    def setup_output_blocks(self, setup: OutputBlockSetupCallback):
        setup([
                FanSetPercentageOutputBlock,
                FanIncreaseSpeedOutputBlock,
                FanDecreaseSpeedOutputBlock,
            ]
        )
