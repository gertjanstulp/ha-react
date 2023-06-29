from custom_components.react.plugin.factory import InputBlockSetupCallback
from custom_components.react.plugin.system.setup import Setup as SystemSetup
from custom_components.react.plugin.system.input.hass_shutdown_input_block import SystemHassEventShutdownInputBlock
from custom_components.react.plugin.system.input.hass_start_input_block import SystemHassEventStartInputBlock
from custom_components.react.plugin.system.input.hass_started_input_block import SystemHassEventStartedInputBlock
from tests._plugins.common import HassApiMockExtend

from tests.const import TEST_CONFIG

SKIP_START_INPUT_BLOCK = "skip_start_input_block"
SKIP_STARTED_INPUT_BLOCK = "skip_started_input_block"


class Setup(SystemSetup, HassApiMockExtend):

    def setup(self):
        test_config: dict = self.hass_api_mock.hass_get_data(TEST_CONFIG, {})
        self.skip_start_input_block = test_config.get(SKIP_START_INPUT_BLOCK, False)
        self.skip_started_input_block = test_config.get(SKIP_STARTED_INPUT_BLOCK, False)


    def setup_input_blocks(self, setup: InputBlockSetupCallback):
        input_blocks = []
        if not self.skip_start_input_block:
            input_blocks.append(SystemHassEventStartInputBlock)
        if not self.skip_started_input_block:
            input_blocks.append(SystemHassEventStartedInputBlock)
        input_blocks.append(SystemHassEventShutdownInputBlock)
        setup(input_blocks)
