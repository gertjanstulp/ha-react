import voluptuous as vol

from homeassistant.helpers import config_validation as cv

from custom_components.react.plugin.const import PROVIDER_TYPE_STATE
from custom_components.react.plugin.factory import ApiSetupCallback, InputBlockSetupCallback, OutputBlockSetupCallback, PluginSetup, ProviderSetupCallback
from custom_components.react.plugin.state.api import StateApi
from custom_components.react.plugin.state.config import StateConfig
from custom_components.react.plugin.state.const import (
    ATTR_STATE_PROVIDER,
    STATE_GENERIC_PROVIDER
)
from custom_components.react.plugin.state.provider import StateProvider
from custom_components.react.plugin.state.input.state_change_input_block import StateChangeInputBlock
from custom_components.react.plugin.state.output.track_state_output_block import TrackStateOutputBlock
from custom_components.react.utils.logger import get_react_logger

_LOGGER = get_react_logger()

WARN_MESSAGE = "WARNING: The state plugin is for troubleshooting purposes only. Do NOT use regularly as it generates a lot of events and could potentially overload the system."

STATE_PLUGIN_CONFIG_SCHEMA = vol.Schema({
    vol.Optional(ATTR_STATE_PROVIDER) : cv.string,
})


class Setup(PluginSetup[StateConfig]):
    def __init__(self) -> None:
        super().__init__(STATE_PLUGIN_CONFIG_SCHEMA)


    def setup(self):
        _LOGGER.warn(WARN_MESSAGE)
    

    def setup_config(self, raw_config: dict) -> StateConfig:
        return StateConfig(raw_config)
    

    def setup_api(self, setup: ApiSetupCallback):
        setup(StateApi)


    def setup_provider(self, setup: ProviderSetupCallback):
        setup(StateProvider, PROVIDER_TYPE_STATE, STATE_GENERIC_PROVIDER)


    def setup_input_blocks(self, setup: InputBlockSetupCallback):
        setup(StateChangeInputBlock)


    def setup_output_blocks(self, setup: OutputBlockSetupCallback):
        setup(TrackStateOutputBlock)
