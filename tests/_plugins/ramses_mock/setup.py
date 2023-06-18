from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import Context

from custom_components.react.plugin.factory import ProviderSetupCallback
from custom_components.react.plugin.ramses.setup import Setup as RamsesSetup

from tests._plugins.common import HassApiMockExtend
from tests.const import (
    ATTR_ENTITY_STATE,
    ATTR_ENTITY_STATE_ATTRIBUTES,
    TEST_CONFIG,
)
from tests.tst_context import TstContext

RAMSES_MOCK_PROVIDER = "ramses_mock"

class Setup(RamsesSetup, HassApiMockExtend):
    def setup(self):
        test_config: dict = self.hass_api_mock.hass_get_data(TEST_CONFIG, {})
        climate_entity_id = test_config.get(ATTR_ENTITY_ID)
        climate_state = test_config.get(ATTR_ENTITY_STATE, None)
        climate_state_attributes = test_config.get(ATTR_ENTITY_STATE_ATTRIBUTES, None)
        if climate_entity_id and climate_state != None:
            self.hass_api_mock.hass_register_state(climate_entity_id, climate_state, climate_state_attributes)
