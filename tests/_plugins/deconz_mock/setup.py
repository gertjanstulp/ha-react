from custom_components.react.plugin.deconz.setup import Setup as DeconzSetup

from tests._plugins.common import HassApiMockExtend
from tests.const import (
    TEST_CONFIG
)


class Setup(DeconzSetup, HassApiMockExtend):
    def setup(self):
        test_config: dict = self.hass_api_mock.hass_get_data(TEST_CONFIG, {})
