from datetime import datetime
from typing import Any

from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import Context

from custom_components.react.const import (
    ATTR_NEW_STATE, 
    ATTR_OLD_STATE, 
    ATTR_TIMESTAMP,
)
from custom_components.react.plugin.const import PROVIDER_TYPE_STATE
from custom_components.react.plugin.factory import ProviderSetupCallback
from custom_components.react.plugin.state.setup import Setup as StateSetup
from custom_components.react.plugin.state.provider import StateProvider

from tests._plugins.common import HassApiMockExtend
from tests.common import TEST_CONTEXT
from tests.const import (
    ATTR_ENTITY_STATE, 
    ATTR_SETUP_MOCK_PROVIDER, 
    TEST_CONFIG,
)
from tests.tst_context import TstContext

STATE_MOCK_PROVIDER = "state_mock"


class Setup(StateSetup, HassApiMockExtend):
    def setup(self):
        super().setup()

        test_config: dict = self.hass_api_mock.hass_get_data(TEST_CONFIG, {})
        self.setup_mock_provider = test_config.get(ATTR_SETUP_MOCK_PROVIDER, False)
        
        state_entity_id = test_config.get(ATTR_ENTITY_ID)
        state_state = test_config.get(ATTR_ENTITY_STATE, None)
        if state_entity_id and state_state != None:
            self.hass_api_mock.hass_register_state(state_entity_id, state_state)


    def setup_provider(self, setup: ProviderSetupCallback):
        if self.setup_mock_provider:
            setup(StateProviderMock, PROVIDER_TYPE_STATE, STATE_MOCK_PROVIDER)
        else:
            super().setup_provider(setup)
    

class StateProviderMock(StateProvider):

    async def async_track_entity_state_change(self, context: Context, entity_id: str, old_state: Any, new_state: Any, timestamp: datetime):
        test_context: TstContext = self.plugin.hass_api.hass_get_data(TEST_CONTEXT)
        data = {
            ATTR_ENTITY_ID: entity_id,
            ATTR_OLD_STATE: old_state,
            ATTR_NEW_STATE: new_state,
            ATTR_TIMESTAMP: timestamp,
        }
        test_context.register_plugin_data(data)
