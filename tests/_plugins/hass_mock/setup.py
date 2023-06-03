from custom_components.react.plugin.factory import InputBlockSetupCallback
from custom_components.react.plugin.hass.setup import Setup as HassSetup
from custom_components.react.plugin.hass.input.shutdown_input_block import HassEventShutdownInputBlock
from custom_components.react.plugin.hass.input.start_input_block import HassEventStartInputBlock
from custom_components.react.plugin.hass.input.started_input_block import HassEventStartedInputBlock
from tests._plugins.common import HassApiMockExtend

from tests.const import TEST_CONFIG

SKIP_START_INPUT_BLOCK = "skip_start_input_block"
SKIP_STARTED_INPUT_BLOCK = "skip_started_input_block"


class Setup(HassSetup, HassApiMockExtend):

    def setup(self):
        test_config: dict = self.hass_api_mock.hass_get_data(TEST_CONFIG, {})
        self.skip_start_input_block = test_config.get(SKIP_START_INPUT_BLOCK, False)
        self.skip_started_input_block = test_config.get(SKIP_STARTED_INPUT_BLOCK, False)


    def setup_input_blocks(self, setup: InputBlockSetupCallback):
        input_blocks = []
        if not self.skip_start_input_block:
            input_blocks.append(HassEventStartInputBlock)
        if not self.skip_started_input_block:
            input_blocks.append(HassEventStartedInputBlock)
        input_blocks.append(HassEventShutdownInputBlock)
        setup(input_blocks)
