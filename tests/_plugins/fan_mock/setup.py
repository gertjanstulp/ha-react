from homeassistant.components.fan import (
    ATTR_PERCENTAGE,
    ATTR_PERCENTAGE_STEP,
)
from homeassistant.const import(
    ATTR_ENTITY_ID,
    ATTR_STATE
)
from homeassistant.core import Context

from custom_components.react.plugin.const import PROVIDER_TYPE_FAN
from custom_components.react.plugin.factory import ProviderSetupCallback
from custom_components.react.plugin.fan.setup import Setup as FanSetup
from custom_components.react.plugin.fan.provider import FanProvider
from custom_components.react.utils.session import Session

from tests._plugins.common import HassApiMockExtend
from tests.common import TEST_CONTEXT
from tests.const import (
    ATTR_ENTITY_STATE,
    ATTR_ENTITY_STATE_ATTRIBUTES, 
    ATTR_SETUP_MOCK_PROVIDER, 
    TEST_CONFIG,
)
from tests.tst_context import TstContext

FAN_MOCK_PROVIDER = "fan_mock"


class Setup(FanSetup, HassApiMockExtend):

    def setup(self):
        test_config: dict = self.hass_api_mock.hass_get_data(TEST_CONFIG, {})
        self.setup_mock_provider = test_config.get(ATTR_SETUP_MOCK_PROVIDER, False)
        
        fan_entity_id = test_config.get(ATTR_ENTITY_ID)
        fan_state = test_config.get(ATTR_ENTITY_STATE, None)
        fan_state_attributes = test_config.get(ATTR_ENTITY_STATE_ATTRIBUTES, None)
        if fan_entity_id and fan_state != None:
            self.hass_api_mock.hass_register_state(fan_entity_id, fan_state, fan_state_attributes)


    def setup_provider(self, setup: ProviderSetupCallback):
        if self.setup_mock_provider:
            setup(FanProviderMock, PROVIDER_TYPE_FAN, FAN_MOCK_PROVIDER)
        else:
            super().setup_provider(setup)
    

class FanProviderMock(FanProvider):
    async def async_set_percentage(self, session: Session, context: Context, entity_id: str, percentage: int):
        test_context: TstContext = self.plugin.hass_api.hass_get_data(TEST_CONTEXT)
        data = {
            ATTR_ENTITY_ID: entity_id,
            ATTR_PERCENTAGE: percentage,
        }
        test_context.register_plugin_data(data)
    

    async def async_increase_speed(self, session: Session, context: Context, entity_id: str, percentage_step: int = None):
        test_context: TstContext = self.plugin.hass_api.hass_get_data(TEST_CONTEXT)
        data = {
            ATTR_ENTITY_ID: entity_id,
            ATTR_PERCENTAGE_STEP: percentage_step,
        }
        test_context.register_plugin_data(data)
    

    async def async_decrease_speed(self, session: Session, context: Context, entity_id: str, percentage_step: int = None):
        test_context: TstContext = self.plugin.hass_api.hass_get_data(TEST_CONTEXT)
        data = {
            ATTR_ENTITY_ID: entity_id,
            ATTR_PERCENTAGE_STEP: percentage_step,
        }
        test_context.register_plugin_data(data)
