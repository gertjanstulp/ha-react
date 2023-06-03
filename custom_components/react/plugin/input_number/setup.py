import voluptuous as vol

from homeassistant.helpers import config_validation as cv

from custom_components.react.plugin.const import PROVIDER_TYPE_INPUT_NUMBER
from custom_components.react.plugin.factory import ApiSetupCallback, InputBlockSetupCallback, OutputBlockSetupCallback, PluginSetup, ProviderSetupCallback
from custom_components.react.plugin.input_number.api import InputNumberApi
from custom_components.react.plugin.input_number.config import InputNumberConfig
from custom_components.react.plugin.input_number.const import (
    ATTR_INPUT_NUMBER_PROVIDER, 
    INPUT_NUMBER_GENERIC_PROVIDER
)
from custom_components.react.plugin.input_number.output.decrease_output_block import InputNumberDecreaseOutputBlock
from custom_components.react.plugin.input_number.output.increase_output_block import InputNumberIncreaseOutputBlock
from custom_components.react.plugin.input_number.output.set_output_block import InputNumberSetOutputBlock
from custom_components.react.plugin.input_number.provider import InputNumberProvider
from custom_components.react.plugin.input_number.input.state_change_input_block import InputNumberStateChangeInputBlock


INPUT_NUMBER_PLUGIN_CONFIG_SCHEMA = vol.Schema({
    vol.Optional(ATTR_INPUT_NUMBER_PROVIDER) : cv.string,
})


class Setup(PluginSetup[InputNumberConfig]):
    def __init__(self) -> None:
        super().__init__(INPUT_NUMBER_PLUGIN_CONFIG_SCHEMA)


    def setup_config(self, raw_config: dict) -> InputNumberConfig:
        return InputNumberConfig(raw_config)
    

    def setup_api(self, setup: ApiSetupCallback):
        setup(InputNumberApi)

    
    def setup_provider(self, setup: ProviderSetupCallback):
        setup(InputNumberProvider, PROVIDER_TYPE_INPUT_NUMBER, INPUT_NUMBER_GENERIC_PROVIDER)


    def setup_input_blocks(self, setup: InputBlockSetupCallback):
        setup(InputNumberStateChangeInputBlock)


    def setup_output_blocks(self, setup: OutputBlockSetupCallback):
        setup(
            [
                InputNumberIncreaseOutputBlock,
                InputNumberDecreaseOutputBlock,
                InputNumberSetOutputBlock,
            ],
        )
