import voluptuous as vol

from homeassistant.helpers import config_validation as cv

from custom_components.react.plugin.const import PROVIDER_TYPE_INPUT_BOOLEAN
from custom_components.react.plugin.factory import ApiSetupCallback, InputBlockSetupCallback, OutputBlockSetupCallback, PluginSetup, ProviderSetupCallback
from custom_components.react.plugin.input_boolean.api import InputBooleanApi
from custom_components.react.plugin.input_boolean.config import InputBooleanConfig
from custom_components.react.plugin.input_boolean.const import (
    ATTR_INPUT_BOOLEAN_PROVIDER, 
    INPUT_BOOLEAN_GENERIC_PROVIDER
)
from custom_components.react.plugin.input_boolean.input.state_change_input_block import InputBooleanStateChangeInputBlock
from custom_components.react.plugin.input_boolean.output.toggle_output_block import InputBooleanToggleOutputBlock
from custom_components.react.plugin.input_boolean.output.turn_off_output_block import InputBooleanTurnOffOutputBlock
from custom_components.react.plugin.input_boolean.output.turn_on_output_block import InputBooleanTurnOnOutputBlock
from custom_components.react.plugin.input_boolean.provider import InputBooleanProvider


INPUT_BOOLEAN_PLUGIN_CONFIG_SCHEMA = vol.Schema({
    vol.Optional(ATTR_INPUT_BOOLEAN_PROVIDER) : cv.string,
})


class Setup(PluginSetup[InputBooleanConfig]):
    def __init__(self) -> None:
        super().__init__(INPUT_BOOLEAN_PLUGIN_CONFIG_SCHEMA)


    def setup_config(self, raw_config: dict) -> InputBooleanConfig:
        return InputBooleanConfig(raw_config)
    

    def setup_api(self, setup: ApiSetupCallback):
        setup(InputBooleanApi)

    
    def setup_provider(self, setup: ProviderSetupCallback):
        setup(InputBooleanProvider, PROVIDER_TYPE_INPUT_BOOLEAN, INPUT_BOOLEAN_GENERIC_PROVIDER)


    def setup_input_blocks(self, setup: InputBlockSetupCallback):
        setup(InputBooleanStateChangeInputBlock)


    def setup_output_blocks(self, setup: OutputBlockSetupCallback):
        setup(
            [
                InputBooleanTurnOnOutputBlock,
                InputBooleanTurnOffOutputBlock,
                InputBooleanToggleOutputBlock,
            ],
        )
    