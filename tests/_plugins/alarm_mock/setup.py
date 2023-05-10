from homeassistant.const import (
    ATTR_CODE, 
    ATTR_ENTITY_ID
)
from homeassistant.core import Context

from custom_components.react.const import ATTR_MODE
from custom_components.react.plugin.alarm_control_panel.const import ArmMode
from custom_components.react.plugin.alarm_control_panel.setup import Setup as AlarmSetup
from custom_components.react.plugin.alarm_control_panel.provider import AlarmProvider
from custom_components.react.plugin.const import PROVIDER_TYPE_ALARM_CONTROL_PANEL
from custom_components.react.plugin.factory import ProviderSetupCallback

from tests._plugins.common import HassApiMockExtend
from tests.common import TEST_CONTEXT
from tests.const import ATTR_SETUP_MOCK_PROVIDER, TEST_CONFIG
from tests.tst_context import TstContext

ALARM_MOCK_PROVIDER = "alarm_mock"
ATTR_ALARM_STATE = "alarm_state"


class Setup(AlarmSetup, HassApiMockExtend):

    def setup(self):
        test_config: dict = self.hass_api_mock.hass_get_data(TEST_CONFIG, {})
        self.setup_mock_provider = test_config.get(ATTR_SETUP_MOCK_PROVIDER, False)
        alarm_entity_id = test_config.get(ATTR_ENTITY_ID)
        alarm_state = test_config.get(ATTR_ALARM_STATE, None)
        if alarm_entity_id and alarm_state:
            self.hass_api_mock.hass_register_state(alarm_entity_id, alarm_state)


    def setup_provider(self, setup: ProviderSetupCallback):
        if self.setup_mock_provider:
            setup(AlarmProviderMock, PROVIDER_TYPE_ALARM_CONTROL_PANEL, ALARM_MOCK_PROVIDER)
        else:
            super().setup_provider(setup)


class AlarmProviderMock(AlarmProvider):

    async def async_arm(self, context: Context, entity_id: str, code: str, arm_mode: ArmMode):
        test_context: TstContext = self.plugin.hass_api.hass_get_data(TEST_CONTEXT)
        test_context.register_plugin_data({
            ATTR_ENTITY_ID: entity_id,
            ATTR_CODE: code,
            ATTR_MODE: arm_mode,
        })

    
    async def async_disarm(self, context: Context, entity_id: str, code: str):
        test_context: TstContext = self.plugin.hass_api.hass_get_data(TEST_CONTEXT)
        test_context.register_plugin_data({
            ATTR_ENTITY_ID: entity_id,
            ATTR_CODE: code
        })


    async def async_trigger(self, context: Context, entity_id: str):
        test_context: TstContext = self.plugin.hass_api.hass_get_data(TEST_CONTEXT)
        test_context.register_plugin_data({
            ATTR_ENTITY_ID: entity_id,
        })