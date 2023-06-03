from homeassistant.components.input_text import ATTR_VALUE
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import Context

from custom_components.react.plugin.const import PROVIDER_TYPE_INPUT_TEXT
from custom_components.react.plugin.factory import ProviderSetupCallback
from custom_components.react.plugin.input_text.setup import Setup as InputTextSetup
from custom_components.react.plugin.input_text.provider import InputTextProvider

from tests._plugins.common import HassApiMockExtend
from tests.common import TEST_CONTEXT
from tests.const import (
    ATTR_ENTITY_STATE, 
    ATTR_SETUP_MOCK_PROVIDER, 
    TEST_CONFIG,
)
from tests.tst_context import TstContext

INPUT_TEXT_MOCK_PROVIDER = "input_text_mock"


class Setup(InputTextSetup, HassApiMockExtend):
    
    def setup(self):
        test_config: dict = self.hass_api_mock.hass_get_data(TEST_CONFIG, {})
        self.setup_mock_provider = test_config.get(ATTR_SETUP_MOCK_PROVIDER, False)
        
        input_text_entity_id = test_config.get(ATTR_ENTITY_ID)
        input_text_state = test_config.get(ATTR_ENTITY_STATE, None)
        if input_text_entity_id and input_text_state != None:
            self.hass_api_mock.hass_register_state(input_text_entity_id, input_text_state)


    def setup_provider(self, setup: ProviderSetupCallback):
        if self.setup_mock_provider:
            setup(InputTextProviderMock, PROVIDER_TYPE_INPUT_TEXT, INPUT_TEXT_MOCK_PROVIDER)
        else:
            super().setup_provider(setup)


class InputTextProviderMock(InputTextProvider):

    async def async_input_text_set_value(self, context: Context, entity_id: str, value: str):
        test_context: TstContext = self.plugin.hass_api.hass_get_data(TEST_CONTEXT)
        data = {
            ATTR_ENTITY_ID: entity_id,
            ATTR_VALUE: value,
        }
        test_context.register_plugin_data(data)
