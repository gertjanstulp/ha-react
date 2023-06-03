import voluptuous as vol

from homeassistant.helpers import config_validation as cv

from custom_components.react.plugin.const import PROVIDER_TYPE_INPUT_TEXT
from custom_components.react.plugin.factory import ApiSetupCallback, InputBlockSetupCallback, OutputBlockSetupCallback, PluginSetup, ProviderSetupCallback
from custom_components.react.plugin.input_text.api import InputTextApi
from custom_components.react.plugin.input_text.config import InputTextConfig
from custom_components.react.plugin.input_text.const import (
    ATTR_INPUT_TEXT_PROVIDER, 
    INPUT_TEXT_GENERIC_PROVIDER
)
from custom_components.react.plugin.input_text.provider import InputTextProvider
from custom_components.react.plugin.input_text.output.set_input_block import InputTextSetInputBlock
from custom_components.react.plugin.input_text.input.state_change_input_block import InputTextStateChangeInputBlock


INPUT_TEXT_PLUGIN_CONFIG_SCHEMA = vol.Schema({
    vol.Optional(ATTR_INPUT_TEXT_PROVIDER) : cv.string,
})


class Setup(PluginSetup[InputTextConfig]):
    def __init__(self) -> None:
        super().__init__(INPUT_TEXT_PLUGIN_CONFIG_SCHEMA)


    def setup_config(self, raw_config: dict) -> InputTextConfig:
        return InputTextConfig(raw_config)
    

    def setup_api(self, setup: ApiSetupCallback):
        setup(InputTextApi)

    
    def setup_provider(self, setup: ProviderSetupCallback):
        setup(InputTextProvider, PROVIDER_TYPE_INPUT_TEXT, INPUT_TEXT_GENERIC_PROVIDER)


    def setup_input_blocks(self, setup: InputBlockSetupCallback):
        setup(InputTextStateChangeInputBlock)


    def setup_output_blocks(self, setup: OutputBlockSetupCallback):
        setup(InputTextSetInputBlock)
