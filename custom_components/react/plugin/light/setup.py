import voluptuous as vol

from homeassistant.helpers import config_validation as cv

from custom_components.react.plugin.const import PROVIDER_TYPE_LIGHT
from custom_components.react.plugin.factory import ApiSetupCallback, InputBlockSetupCallback, OutputBlockSetupCallback, PluginSetup, ProviderSetupCallback
from custom_components.react.plugin.light.api import LightApi
from custom_components.react.plugin.light.config import LightConfig
from custom_components.react.plugin.light.const import (
    ATTR_LIGHT_PROVIDER, 
    LIGHT_GENERIC_PROVIDER
)
from custom_components.react.plugin.light.provider import LightProvider
from custom_components.react.plugin.light.input.state_change_input_block import LightStateChangeInputBlock
from custom_components.react.plugin.light.output.turn_on_output_block import LightTurnOnOutputBlock
from custom_components.react.plugin.light.output.turn_off_output_block import LightTurnOffOutputBlock
from custom_components.react.plugin.light.output.toggle_output_block import LightToggleOutputBlock


LIGHT_PLUGIN_CONFIG_SCHEMA = vol.Schema({
    vol.Optional(ATTR_LIGHT_PROVIDER) : cv.string,
})


class Setup(PluginSetup[LightConfig]):
    def __init__(self) -> None:
        super().__init__(LIGHT_PLUGIN_CONFIG_SCHEMA)


    def setup_config(self, raw_config: dict) -> LightConfig:
        return LightConfig(raw_config)
    

    def setup_api(self, setup: ApiSetupCallback):
        setup(LightApi)


    def setup_provider(self, setup: ProviderSetupCallback):
        setup(LightProvider, PROVIDER_TYPE_LIGHT, LIGHT_GENERIC_PROVIDER)
    

    def setup_input_blocks(self, setup: InputBlockSetupCallback):
        setup(LightStateChangeInputBlock)


    def setup_output_blocks(self, setup: OutputBlockSetupCallback):
        setup([
                LightTurnOnOutputBlock,
                LightTurnOffOutputBlock,
                LightToggleOutputBlock,
            ]
        )
