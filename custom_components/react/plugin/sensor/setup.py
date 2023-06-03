from custom_components.react.plugin.sensor.input.state_change_input_block import SensorStateChangeInputBlock

from custom_components.react.plugin.factory import InputBlockSetupCallback, PluginSetup
from custom_components.react.utils.struct import DynamicData


class Setup(PluginSetup[DynamicData]):

    def setup_input_blocks(self, setup: InputBlockSetupCallback):
        setup(SensorStateChangeInputBlock)
