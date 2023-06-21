from custom_components.react.plugin.factory import InputBlockSetupCallback, PluginSetup
from custom_components.react.plugin.time.input.sunrise_input_block import SunriseInputBlock
from custom_components.react.plugin.time.input.sunset_input_block import SunsetInputBlock
from custom_components.react.plugin.time.input.time_input_block import TimeInputBlock


class Setup(PluginSetup):

    def setup_input_blocks(self, setup: InputBlockSetupCallback):
        setup([
            TimeInputBlock,
            SunsetInputBlock,
            SunriseInputBlock,
        ])
