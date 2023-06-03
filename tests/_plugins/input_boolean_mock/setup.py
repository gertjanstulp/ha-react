from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import Context

from custom_components.react.const import ATTR_STATE
from custom_components.react.plugin.const import PROVIDER_TYPE_INPUT_BOOLEAN
from custom_components.react.plugin.factory import ProviderSetupCallback
from custom_components.react.plugin.input_boolean.setup import Setup as InputBooleanSetup
from custom_components.react.plugin.input_boolean.provider import InputBooleanProvider

from tests._plugins.common import HassApiMockExtend
from tests.common import TEST_CONTEXT
from tests.const import (
    ATTR_ENTITY_STATE, 
    ATTR_SETUP_MOCK_PROVIDER, 
    TEST_CONFIG,
)
from tests.tst_context import TstContext


INPUT_BOOLEAN_MOCK_PROVIDER = "input_boolean_mock"


class Setup(InputBooleanSetup, HassApiMockExtend):
    
    def setup(self):
        test_config: dict = self.hass_api_mock.hass_get_data(TEST_CONFIG, {})
        self.setup_mock_provider = test_config.get(ATTR_SETUP_MOCK_PROVIDER, False)

        input_boolean_entity_id = test_config.get(ATTR_ENTITY_ID)
        input_boolean_state = test_config.get(ATTR_ENTITY_STATE, None)
        if input_boolean_entity_id and input_boolean_state != None:
            self.hass_api_mock.hass_register_state(input_boolean_entity_id, input_boolean_state)


    def setup_provider(self, setup: ProviderSetupCallback):
        if self.setup_mock_provider:
            setup(InputBooleanProviderMock, PROVIDER_TYPE_INPUT_BOOLEAN, INPUT_BOOLEAN_MOCK_PROVIDER)
        else:
            super().setup_provider(setup)


class InputBooleanProviderMock(InputBooleanProvider):

    async def async_input_boolean_set_value(self, context: Context, entity_id: str, value: bool):
        test_context: TstContext = self.plugin.hass_api.hass_get_data(TEST_CONTEXT)
        data = {
            ATTR_ENTITY_ID: entity_id,
            ATTR_STATE: value,
        }
        test_context.register_plugin_data(data)