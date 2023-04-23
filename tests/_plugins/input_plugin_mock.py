from homeassistant.components.input_number import (
    ATTR_VALUE as NUMBER_ATTR_VALUE,
)
from homeassistant.components.input_text import (
    ATTR_VALUE as TEXT_ATTR_VALUE
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import Context
from custom_components.react.const import ATTR_STATE
from custom_components.react.plugin.const import PROVIDER_TYPE_INPUT

from custom_components.react.plugin.input.plugin import load as load_plugin
from custom_components.react.plugin.input.provider import InputProvider
from custom_components.react.plugin.plugin_factory import HassApi, PluginApi
from custom_components.react.utils.struct import DynamicData

from tests._plugins.common import HassApiMock
from tests.common import TEST_CONTEXT
from tests.const import ATTR_ENTITY_STATE, ATTR_INPUT_PROVIDER
from tests.tst_context import TstContext


INPUT_MOCK_PROVIDER = "input_mock"


def load(plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
    hass_api_mock = HassApiMock(hass_api.hass)
    load_plugin(plugin_api, hass_api_mock, config)
    if input_provider := config.get(ATTR_INPUT_PROVIDER, None):
        setup_mock_provider(plugin_api, hass_api, input_provider)
    input_entity_id = config.get(ATTR_ENTITY_ID)
    input_state = config.get(ATTR_ENTITY_STATE, None)
    if input_entity_id and input_state != None:
        hass_api_mock.hass_register_state(input_entity_id, input_state)


def setup_mock_provider(plugin_api: PluginApi, hass_api: HassApi, input_provider: str):
    plugin_api.register_plugin_provider(
        PROVIDER_TYPE_INPUT, 
        input_provider,
        InputProviderMock(plugin_api, hass_api))


class InputProviderMock(InputProvider):
    def __init__(self, plugin_api: PluginApi, hass_api: HassApi) -> None:
        super().__init__(plugin_api, hass_api)

        
    async def async_input_number_set_value(self, context: Context, entity_id: str, value: float):
        tc: TstContext = self.hass_api.hass_get_data(TEST_CONTEXT)
        data = {
            ATTR_ENTITY_ID: entity_id,
            NUMBER_ATTR_VALUE: value,
        }
        tc.register_plugin_data(data)


    async def async_input_text_set_value(self, context: Context, entity_id: str, value: str):
        tc: TstContext = self.hass_api.hass_get_data(TEST_CONTEXT)
        data = {
            ATTR_ENTITY_ID: entity_id,
            TEXT_ATTR_VALUE: value,
        }
        tc.register_plugin_data(data)


    async def async_input_boolean_set_value(self, context: Context, entity_id: str, value: bool):
        tc: TstContext = self.hass_api.hass_get_data(TEST_CONTEXT)
        data = {
            ATTR_ENTITY_ID: entity_id,
            ATTR_STATE: value,
        }
        tc.register_plugin_data(data)