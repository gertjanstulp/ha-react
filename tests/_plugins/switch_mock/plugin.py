from homeassistant.const import(
    ATTR_ENTITY_ID,
    ATTR_STATE
)
from homeassistant.core import Context

from custom_components.react.plugin.api import HassApi, PluginApi
from custom_components.react.plugin.const import PROVIDER_TYPE_SWITCH
from custom_components.react.plugin.switch.const import ATTR_SWITCH_PROVIDER
from custom_components.react.plugin.switch.plugin import Plugin as SwitchPlugin
from custom_components.react.plugin.switch.provider import SwitchProvider
from custom_components.react.utils.struct import DynamicData

from tests._plugins.common import HassApiMock
from tests.common import TEST_CONTEXT
from tests.const import (
    ATTR_ENTITY_STATE, 
    TEST_CONFIG
)
from tests.tst_context import TstContext


SWITCH_MOCK_PROVIDER = "switch_mock"


class Plugin(SwitchPlugin):
    def load(self, plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
        hass_api_mock = HassApiMock(hass_api.hass)
        super().load(plugin_api, hass_api_mock, config)
        if switch_provider := config.get(ATTR_SWITCH_PROVIDER, None):
            setup_mock_provider(plugin_api, hass_api, switch_provider)
        
        test_config: dict = hass_api.hass_get_data(TEST_CONFIG, {})
        switch_entity_id = test_config.get(ATTR_ENTITY_ID)
        switch_state = test_config.get(ATTR_ENTITY_STATE, None)
        if switch_entity_id and switch_state != None:
            hass_api_mock.hass_register_state(switch_entity_id, switch_state)


def setup_mock_provider(plugin_api: PluginApi, hass_api: HassApi, switch_provider: str):
    plugin_api.register_plugin_provider(
        PROVIDER_TYPE_SWITCH, 
        switch_provider,
        SwitchProviderMock(plugin_api, hass_api))
        

class SwitchProviderMock(SwitchProvider):
    def __init__(self, plugin_api: PluginApi, hass_api: HassApi) -> None:
        super().__init__(plugin_api, hass_api)


    async def async_set_state(self, context: Context, entity_id: str, state: str):
        test_context: TstContext = self.hass_api.hass_get_data(TEST_CONTEXT)
        data = {
            ATTR_ENTITY_ID: entity_id,
            ATTR_STATE: state,
        }
        test_context.register_plugin_data(data)