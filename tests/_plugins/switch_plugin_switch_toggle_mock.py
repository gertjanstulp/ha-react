from homeassistant.core import Context
from homeassistant.const import (
    ATTR_ENTITY_ID, 
    STATE_UNKNOWN,
)

from custom_components.react.base import ReactBase
from custom_components.react.const import ATTR_STATE
from custom_components.react.plugin.switch.tasks.switch_toggle_task import SwitchToggleTask
from custom_components.react.plugin.plugin_factory import PluginApi
from custom_components.react.utils.struct import DynamicData
from tests.common import TEST_CONTEXT
from tests.tst_context import TstContext


def load(plugin_api: PluginApi, config: DynamicData):
    plugin_api.register_plugin_task(SwitchToggleTaskMock)


class SwitchApiMock():
    def __init__(self, react: ReactBase) -> None:
        self.react = react


    async def async_switch_toggle(self, context: Context, entity_id: str):
        tc: TstContext = self.react.hass.data[TEST_CONTEXT]
        tc.register_plugin_data({
            ATTR_ENTITY_ID: entity_id,
            ATTR_STATE: STATE_UNKNOWN,
        })


class SwitchToggleTaskMock(SwitchToggleTask):

    def __init__(self, react: ReactBase) -> None:
        api = SwitchApiMock(react)
        super().__init__(react, api)