from custom_components.react.plugin.esphome.setup import Setup as EspHomeSetup

from tests._plugins.common import HassApiMockExtend
from tests.const import (
    TEST_CONFIG
)


class Setup(EspHomeSetup, HassApiMockExtend):
    def setup(self):
        test_config: dict = self.hass_api_mock.hass_get_data(TEST_CONFIG, {})
