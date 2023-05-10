from custom_components.react.plugin.factory import InputBlockSetupCallback, PluginSetup
from custom_components.react.plugin.input_button.input.state_change_input_block import InputButtonStateChangeInputBlock


class Setup(PluginSetup):
    def setup_input_blocks(self, setup: InputBlockSetupCallback):
        setup(InputButtonStateChangeInputBlock)
