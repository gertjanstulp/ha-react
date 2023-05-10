from homeassistant.const import(
    ATTR_ENTITY_ID,
    ATTR_STATE
)
from homeassistant.core import Context

from custom_components.react.plugin.const import PROVIDER_TYPE_SWITCH
from custom_components.react.plugin.factory import ProviderSetupCallback
from custom_components.react.plugin.switch.setup import Setup as SwitchSetup
from custom_components.react.plugin.switch.provider import SwitchProvider

from tests._plugins.common import HassApiMockExtend
from tests.common import TEST_CONTEXT
from tests.const import (
    ATTR_ENTITY_STATE, 
    ATTR_SETUP_MOCK_PROVIDER, 
    TEST_CONFIG,
)
from tests.tst_context import TstContext

SWITCH_MOCK_PROVIDER = "switch_mock"


class Setup(SwitchSetup, HassApiMockExtend):

    def setup(self):
        test_config: dict = self.hass_api_mock.hass_get_data(TEST_CONFIG, {})
        self.setup_mock_provider = test_config.get(ATTR_SETUP_MOCK_PROVIDER, False)
        
        switch_entity_id = test_config.get(ATTR_ENTITY_ID)
        switch_state = test_config.get(ATTR_ENTITY_STATE, None)
        if switch_entity_id and switch_state != None:
            self.hass_api_mock.hass_register_state(switch_entity_id, switch_state)


    def setup_provider(self, setup: ProviderSetupCallback):
        if self.setup_mock_provider:
            setup(SwitchProviderMock, PROVIDER_TYPE_SWITCH, SWITCH_MOCK_PROVIDER)
        else:
            super().setup_provider(setup)
    

class SwitchProviderMock(SwitchProvider):

    async def async_set_state(self, context: Context, entity_id: str, state: str):
        test_context: TstContext = self.plugin.hass_api.hass_get_data(TEST_CONTEXT)
        data = {
            ATTR_ENTITY_ID: entity_id,
            ATTR_STATE: state,
        }
        test_context.register_plugin_data(data)
