from homeassistant.components.input_text import (
    ATTR_VALUE
)
from homeassistant.core import Context
from homeassistant.const import (
    ATTR_ENTITY_ID, 
)

from custom_components.react.base import ReactBase
from custom_components.react.plugin.input.tasks.input_text_set_task import InputTextSetTask
from custom_components.react.plugin.plugin_factory import PluginApi
from custom_components.react.utils.struct import DynamicData
from tests.common import TEST_CONTEXT
from tests.tst_context import TstContext


def load(plugin_api: PluginApi, config: DynamicData):
    plugin_api.register_plugin_task(InputTextSetTaskMock)


class InputApiMock():
    def __init__(self, react: ReactBase) -> None:
        self.react = react


    async def async_input_text_set(self, context: Context, entity_id: str, value: float):
        tc: TstContext = self.react.hass.data[TEST_CONTEXT]
        tc.register_plugin_data({
            ATTR_ENTITY_ID: entity_id,
            ATTR_VALUE: value,
        })


class InputTextSetTaskMock(InputTextSetTask):

    def __init__(self, react: ReactBase) -> None:
        api = InputApiMock(react)
        super().__init__(react, api)