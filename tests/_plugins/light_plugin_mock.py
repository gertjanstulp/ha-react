from homeassistant.const import(
    ATTR_ENTITY_ID,
    ATTR_STATE
)
from homeassistant.core import Context

from custom_components.react.base import ReactBase
from custom_components.react.plugin.light.api import Api, ApiConfig
from custom_components.react.plugin.light.tasks.light_toggle_task import LightToggleTask
from custom_components.react.plugin.light.tasks.light_turn_off_task import LightTurnOffTask
from custom_components.react.plugin.light.tasks.light_turn_on_task import LightTurnOnTask
from custom_components.react.plugin.plugin_factory import PluginApi
from custom_components.react.utils.struct import DynamicData
from tests.common import TEST_CONTEXT
from tests.tst_context import TstContext


def load(plugin_api: PluginApi, config: DynamicData):
    api = LightApiMock(plugin_api.react, ApiConfig(config))
    plugin_api.register_plugin_task(LightTurnOnTask, api=api)
    plugin_api.register_plugin_task(LightTurnOffTask, api=api)
    plugin_api.register_plugin_task(LightToggleTask, api=api)


class LightApiMock(Api):
    def __init__(self, react: ReactBase, config: ApiConfig) -> None:
        super().__init__(react, config, LightServiceMock(react))


class LightServiceMock():
    def __init__(self, react: ReactBase) -> None:
        self.react = react


    async def async_set_state(self, context: Context, entity_id: str, state: str):
        tc: TstContext = self.react.hass.data[TEST_CONTEXT]
        data = {
            ATTR_ENTITY_ID: entity_id,
            ATTR_STATE: state,
        }
        tc.register_plugin_data(data)