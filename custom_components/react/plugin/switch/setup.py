import voluptuous as vol

from homeassistant.helpers import config_validation as cv

from custom_components.react.plugin.const import PROVIDER_TYPE_SWITCH
from custom_components.react.plugin.factory import ApiSetupCallback, InputBlockSetupCallback, OutputBlockSetupCallback, PluginSetup, ProviderSetupCallback
from custom_components.react.plugin.switch.api import SwitchApi
from custom_components.react.plugin.switch.config import SwitchConfig
from custom_components.react.plugin.switch.const import (
    ATTR_SWITCH_PROVIDER, 
    SWITCH_GENERIC_PROVIDER
)
from custom_components.react.plugin.switch.provider import SwitchProvider
from custom_components.react.plugin.switch.input.state_change_input_block import SwitchStateChangeInputBlock
from custom_components.react.plugin.switch.output.turn_on_output_block import SwitchTurnOnOutputBlock
from custom_components.react.plugin.switch.output.turn_off_output_block import SwitchTurnOffOutputBlock
from custom_components.react.plugin.switch.output.toggle_output_block import SwitchToggleOutputBlock


SWITCH_PLUGIN_CONFIG_SCHEMA = vol.Schema({
    vol.Optional(ATTR_SWITCH_PROVIDER) : cv.string,
})


class Setup(PluginSetup[SwitchConfig]):
    def __init__(self) -> None:
        super().__init__(SWITCH_PLUGIN_CONFIG_SCHEMA)


    def setup_config(self, raw_config: dict) -> SwitchConfig:
        return SwitchConfig(raw_config)
    

    def setup_api(self, setup: ApiSetupCallback):
        setup(SwitchApi)


    def setup_provider(self, setup: ProviderSetupCallback):
        setup(SwitchProvider, PROVIDER_TYPE_SWITCH, SWITCH_GENERIC_PROVIDER)
    

    def setup_input_blocks(self, setup: InputBlockSetupCallback):
        setup(SwitchStateChangeInputBlock)


    def setup_output_blocks(self, setup: OutputBlockSetupCallback):
        setup([
                SwitchTurnOnOutputBlock,
                SwitchTurnOffOutputBlock,
                SwitchToggleOutputBlock,
            ],
        )
