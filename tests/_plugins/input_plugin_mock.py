from homeassistant.components.input_number import (
    ATTR_VALUE as NUMBER_ATTR_VALUE,
)
from homeassistant.components.input_text import (
    ATTR_VALUE as TEXT_ATTR_VALUE
)
from homeassistant.core import Context
from homeassistant.const import (
    ATTR_ENTITY_ID, 
)

from custom_components.react.base import ReactBase
from custom_components.react.const import ATTR_STATE
from custom_components.react.plugin.input.api import InputApi, InputApiConfig
from custom_components.react.plugin.input.service import InputService
from custom_components.react.plugin.input.tasks.input_boolean_toggle_task import InputBooleanToggleTask
from custom_components.react.plugin.input.tasks.input_boolean_turn_off_task import InputBooleanTurnOffTask
from custom_components.react.plugin.input.tasks.input_boolean_turn_on_task import InputBooleanTurnOnTask
from custom_components.react.plugin.input.tasks.input_number_decrease_task import InputNumberDecreaseTask
from custom_components.react.plugin.input.tasks.input_number_increase_task import InputNumberIncreaseTask
from custom_components.react.plugin.input.tasks.input_number_set_task import InputNumberSetTask
from custom_components.react.plugin.input.tasks.input_text_set_task import InputTextSetTask
from custom_components.react.plugin.plugin_factory import PluginApi
from custom_components.react.utils.struct import DynamicData

from tests.common import TEST_CONTEXT
from tests.tst_context import TstContext


def load(plugin_api: PluginApi, config: DynamicData):
    api = InputApiMock(plugin_api.react, InputApiConfig(config))
    plugin_api.register_plugin_task(InputNumberSetTask, api=api)
    plugin_api.register_plugin_task(InputNumberIncreaseTask, api=api)
    plugin_api.register_plugin_task(InputNumberDecreaseTask, api=api)
    plugin_api.register_plugin_task(InputTextSetTask, api=api)
    plugin_api.register_plugin_task(InputBooleanTurnOnTask, api=api)
    plugin_api.register_plugin_task(InputBooleanTurnOffTask, api=api)
    plugin_api.register_plugin_task(InputBooleanToggleTask, api=api)


class InputApiMock(InputApi):
    def __init__(self, react: ReactBase, config: InputApiConfig) -> None:
        super().__init__(react, config, InputServiceMock(react))


class InputServiceMock(InputService):
    def __init__(self, react: ReactBase) -> None:
        self.react = react

        
    async def async_input_number_set_value(self, context: Context, entity_id: str, value: float):
        await super().async_input_number_set_value(context, entity_id, value)
        tc: TstContext = self.react.hass.data[TEST_CONTEXT]
        data = {
            ATTR_ENTITY_ID: entity_id,
            NUMBER_ATTR_VALUE: value,
        }
        tc.register_plugin_data(data)


    async def async_input_text_set_value(self, context: Context, entity_id: str, value: str):
        await super().async_input_text_set_value(context, entity_id, value)
        tc: TstContext = self.react.hass.data[TEST_CONTEXT]
        data = {
            ATTR_ENTITY_ID: entity_id,
            TEXT_ATTR_VALUE: value,
        }
        tc.register_plugin_data(data)


    async def async_input_boolean_set_value(self, context: Context, entity_id: str, value: bool):
        await super().async_input_boolean_set_value(context, entity_id, value)
        tc: TstContext = self.react.hass.data[TEST_CONTEXT]
        data = {
            ATTR_ENTITY_ID: entity_id,
            ATTR_STATE: value,
        }
        tc.register_plugin_data(data)