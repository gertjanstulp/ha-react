from custom_components.react.plugin.device_tracker.input.state_change_input_block import DeviceTrackerStateChangeInputBlock
from custom_components.react.plugin.factory import InputBlockSetupCallback, PluginSetup


class Setup(PluginSetup):
    def setup_input_blocks(self, setup: InputBlockSetupCallback):
        setup(DeviceTrackerStateChangeInputBlock)
        
