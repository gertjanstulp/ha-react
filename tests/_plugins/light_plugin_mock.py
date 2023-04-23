from homeassistant.const import(
    ATTR_ENTITY_ID,
    ATTR_STATE
)
from homeassistant.core import Context
from custom_components.react.plugin.const import PROVIDER_TYPE_LIGHT

from custom_components.react.plugin.light.plugin import load as load_plugin
from custom_components.react.plugin.light.provider import LightProvider
from custom_components.react.plugin.plugin_factory import HassApi, PluginApi
from custom_components.react.utils.struct import DynamicData

from tests._plugins.common import HassApiMock
from tests.common import TEST_CONTEXT
from tests.const import ATTR_ENTITY_STATE, ATTR_LIGHT_PROVIDER
from tests.tst_context import TstContext


LIGHT_MOCK_PROVIDER = "light_mock"


def load(plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
    hass_api_mock = HassApiMock(hass_api.hass)
    load_plugin(plugin_api, hass_api_mock, config)
    if light_provider := config.get(ATTR_LIGHT_PROVIDER, None):
        setup_mock_provider(plugin_api, hass_api, light_provider)
    light_entity_id = config.get(ATTR_ENTITY_ID)
    light_state = config.get(ATTR_ENTITY_STATE, None)
    if light_entity_id and light_state != None:
        hass_api_mock.hass_register_state(light_entity_id, light_state)


def setup_mock_provider(plugin_api: PluginApi, hass_api: HassApi, light_provider: str):
    plugin_api.register_plugin_provider(
        PROVIDER_TYPE_LIGHT, 
        light_provider,
        LightProviderMock(plugin_api, hass_api))
    

class LightProviderMock(LightProvider):
    def __init__(self, plugin_api: PluginApi, hass_api: HassApi) -> None:
        super().__init__(plugin_api, hass_api)


    async def async_set_state(self, context: Context, entity_id: str, state: str):
        tc: TstContext = self.hass_api.hass_get_data(TEST_CONTEXT)
        data = {
            ATTR_ENTITY_ID: entity_id,
            ATTR_STATE: state,
        }
        tc.register_plugin_data(data)