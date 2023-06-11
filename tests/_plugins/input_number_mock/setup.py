from homeassistant.components.input_number import ATTR_VALUE
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import Context

from custom_components.react.plugin.const import PROVIDER_TYPE_INPUT_NUMBER
from custom_components.react.plugin.factory import ProviderSetupCallback
from custom_components.react.plugin.input_number.setup import Setup as InputNumberSetup
from custom_components.react.plugin.input_number.provider import InputNumberProvider
from custom_components.react.utils.session import Session

from tests._plugins.common import HassApiMockExtend
from tests.common import TEST_CONTEXT
from tests.const import (
    ATTR_ENTITY_STATE, 
    ATTR_SETUP_MOCK_PROVIDER, 
    TEST_CONFIG,
)
from tests.tst_context import TstContext


INPUT_NUMBER_MOCK_PROVIDER = "input_number_mock"


class Setup(InputNumberSetup, HassApiMockExtend):
    
    def setup(self):
        test_config: dict = self.hass_api_mock.hass_get_data(TEST_CONFIG, {})
        self.setup_mock_provider = test_config.get(ATTR_SETUP_MOCK_PROVIDER, False)
        
        input_number_entity_id = test_config.get(ATTR_ENTITY_ID)
        input_number_state = test_config.get(ATTR_ENTITY_STATE, None)
        if input_number_entity_id and input_number_state != None:
            self.hass_api_mock.hass_register_state(input_number_entity_id, input_number_state)


    def setup_provider(self, setup: ProviderSetupCallback):
        if self.setup_mock_provider:
            setup(InputNumberProviderMock, PROVIDER_TYPE_INPUT_NUMBER, INPUT_NUMBER_MOCK_PROVIDER)
        else:
            super().setup_provider(setup)


class InputNumberProviderMock(InputNumberProvider):
        
    async def async_input_number_set_value(self, session: Session, context: Context, entity_id: str, value: float):
        test_context: TstContext = self.plugin.hass_api.hass_get_data(TEST_CONTEXT)
        data = {
            ATTR_ENTITY_ID: entity_id,
            ATTR_VALUE: value,
        }
        test_context.register_plugin_data(data)
