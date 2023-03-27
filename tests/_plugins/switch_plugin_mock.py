from homeassistant.const import(
    ATTR_ENTITY_ID,
    ATTR_STATE
)
from homeassistant.core import Context

from custom_components.react.base import ReactBase
from custom_components.react.plugin.switch.api import SwitchApi, SwitchApiConfig
from custom_components.react.plugin.switch.service import SwitchService
from custom_components.react.plugin.switch.tasks.switch_toggle_task import SwitchToggleTask
from custom_components.react.plugin.switch.tasks.switch_turn_off_task import SwitchTurnOffTask
from custom_components.react.plugin.switch.tasks.switch_turn_on_task import SwitchTurnOnTask
from custom_components.react.plugin.plugin_factory import PluginApi
from custom_components.react.utils.struct import DynamicData
from tests.common import TEST_CONTEXT
from tests.tst_context import TstContext


def load(plugin_api: PluginApi, config: DynamicData):
    api = SwitchApiMock(plugin_api.react, SwitchApiConfig(config))
    plugin_api.register_plugin_task(SwitchTurnOnTask, api=api)
    plugin_api.register_plugin_task(SwitchTurnOffTask, api=api)
    plugin_api.register_plugin_task(SwitchToggleTask, api=api)


class SwitchApiMock(SwitchApi):
    def __init__(self, react: ReactBase, config: SwitchApiConfig) -> None:
        super().__init__(react, config, SwitchServiceMock(react))


class SwitchServiceMock(SwitchService):
    def __init__(self, react: ReactBase) -> None:
        self.react = react


    async def async_set_state(self, context: Context, entity_id: str, state: str):
        await super().async_set_state(context, entity_id, state)
        tc: TstContext = self.react.hass.data[TEST_CONTEXT]
        data = {
            ATTR_ENTITY_ID: entity_id,
            ATTR_STATE: state,
        }
        tc.register_plugin_data(data)