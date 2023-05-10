from custom_components.react.plugin.factory import InputBlockSetupCallback, PluginSetup
from custom_components.react.plugin.hass.input.shutdown_input_block import HassEventShutdownInputBlock
from custom_components.react.plugin.hass.input.start_input_block import HassEventStartInputBlock
from custom_components.react.plugin.hass.input.started_input_block import HassEventStartedInputBlock


class Setup(PluginSetup):
    def setup_input_blocks(self, setup: InputBlockSetupCallback):
        setup([
            HassEventStartInputBlock,
            HassEventStartedInputBlock,
            HassEventShutdownInputBlock,
        ])
