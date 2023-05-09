from homeassistant.const import (
    ATTR_CODE, 
    ATTR_ENTITY_ID
)
from homeassistant.core import Context

from custom_components.react.const import ATTR_MODE
from custom_components.react.plugin.alarm.const import ATTR_ALARM_PROVIDER, ArmMode
from custom_components.react.plugin.alarm.plugin import Plugin as AlarmPlugin
from custom_components.react.plugin.alarm.provider import AlarmProvider
from custom_components.react.plugin.const import PROVIDER_TYPE_ALARM
from custom_components.react.plugin.api import HassApi, PluginApi
from custom_components.react.plugin.factory import PluginBase
from custom_components.react.utils.struct import DynamicData

from tests._plugins.common import HassApiMock
from tests.common import TEST_CONTEXT
from tests.const import TEST_CONFIG
from tests.tst_context import TstContext

ALARM_MOCK_PROVIDER = "alarm_mock"
ATTR_ALARM_STATE = "alarm_state"


class Plugin(AlarmPlugin):
    def load(self, plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
        hass_api_mock = HassApiMock(hass_api.hass)
        super().load(plugin_api, hass_api_mock, config)

        test_config: dict = hass_api.hass_get_data(TEST_CONFIG, {})
        if alarm_provider := config.get(ATTR_ALARM_PROVIDER, None):
            self.setup_mock_provider(plugin_api, hass_api, alarm_provider)
        alarm_entity_id = test_config.get(ATTR_ENTITY_ID)
        alarm_state = test_config.get(ATTR_ALARM_STATE, None)
        if alarm_entity_id and alarm_state:
            hass_api_mock.hass_register_state(alarm_entity_id, alarm_state)


    def setup_mock_provider(self, plugin_api: PluginApi, hass_api: HassApi, alarm_provider: str):
        plugin_api.register_plugin_provider(
            PROVIDER_TYPE_ALARM, 
            alarm_provider,
            AlarmProvidereMock(plugin_api, hass_api))


class AlarmProvidereMock(AlarmProvider):
    def __init__(self, plugin_api: PluginApi, hass_api: HassApi) -> None:
        super().__init__(plugin_api, hass_api)


    async def async_arm(self, context: Context, entity_id: str, code: str, arm_mode: ArmMode):
        test_context: TstContext = self.hass_api.hass_get_data(TEST_CONTEXT)
        test_context.register_plugin_data({
            ATTR_ENTITY_ID: entity_id,
            ATTR_CODE: code,
            ATTR_MODE: arm_mode,
        })

    
    async def async_disarm(self, context: Context, entity_id: str, code: str):
        test_context: TstContext = self.hass_api.hass_get_data(TEST_CONTEXT)
        test_context.register_plugin_data({
            ATTR_ENTITY_ID: entity_id,
            ATTR_CODE: code
        })


    async def async_trigger(self, context: Context, entity_id: str):
        test_context: TstContext = self.hass_api.hass_get_data(TEST_CONTEXT)
        test_context.register_plugin_data({
            ATTR_ENTITY_ID: entity_id,
        })