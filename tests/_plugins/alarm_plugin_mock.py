from homeassistant.const import (
    ATTR_CODE, 
    ATTR_ENTITY_ID
)
from homeassistant.core import Context

from custom_components.react.const import ATTR_MODE
from custom_components.react.plugin.alarm.const import ArmMode
from custom_components.react.plugin.alarm.plugin import load as load_plugin
from custom_components.react.plugin.alarm.provider import AlarmProvider
from custom_components.react.plugin.const import PROVIDER_TYPE_ALARM
from custom_components.react.plugin.plugin_factory import HassApi, PluginApi
from custom_components.react.utils.struct import DynamicData

from tests._plugins.common import HassApiMock
from tests.common import TEST_CONTEXT
from tests.const import ATTR_ALARM_PROVIDER
from tests.tst_context import TstContext

ALARM_MOCK_PROVIDER = "alarm_mock"
ATTR_ALARM_STATE = "alarm_state"


def load(plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
    hass_api_mock = HassApiMock(hass_api.hass)
    load_plugin(plugin_api, hass_api_mock, config)
    if alarm_provider := config.get(ATTR_ALARM_PROVIDER, None):
        setup_mock_provider(plugin_api, hass_api, alarm_provider)
    alarm_entity_id = config.get(ATTR_ENTITY_ID)
    alarm_state = config.get(ATTR_ALARM_STATE, None)
    if alarm_entity_id and alarm_state:
        hass_api_mock.hass_register_state(alarm_entity_id, alarm_state)


def setup_mock_provider(plugin_api: PluginApi, hass_api: HassApi, alarm_provider: str):
    plugin_api.register_plugin_provider(
        PROVIDER_TYPE_ALARM, 
        alarm_provider,
        AlarmProvidereMock(plugin_api, hass_api))


class AlarmProvidereMock(AlarmProvider):
    def __init__(self, plugin_api: PluginApi, hass_api: HassApi) -> None:
        super().__init__(plugin_api, hass_api)


    async def async_arm(self, context: Context, entity_id: str, code: str, arm_mode: ArmMode):
        tc: TstContext = self.hass_api.hass_get_data(TEST_CONTEXT)
        tc.register_plugin_data({
            ATTR_ENTITY_ID: entity_id,
            ATTR_CODE: code,
            ATTR_MODE: arm_mode,
        })

    
    async def async_disarm(self, context: Context, entity_id: str, code: str):
        tc: TstContext = self.hass_api.hass_get_data(TEST_CONTEXT)
        tc.register_plugin_data({
            ATTR_ENTITY_ID: entity_id,
            ATTR_CODE: code
        })


    async def async_trigger(self, context: Context, entity_id: str):
        tc: TstContext = self.hass_api.hass_get_data(TEST_CONTEXT)
        tc.register_plugin_data({
            ATTR_ENTITY_ID: entity_id,
        })