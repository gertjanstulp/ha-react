from homeassistant.core import Context
from homeassistant.const import (
    ATTR_ENTITY_ID, 
)

from homeassistant.const import (
    ATTR_CODE,
)

from custom_components.react.base import ReactBase
from custom_components.react.plugin.alarm.tasks.alarm_trigger_task import AlarmTriggerTask
from custom_components.react.plugin.plugin_factory import PluginApi
from custom_components.react.utils.struct import DynamicData
from tests.common import TEST_CONTEXT, TEST_FLAG_VERIFY_CONFIG
from tests.tst_context import TstContext


def load(plugin_api: PluginApi, config: DynamicData):
    plugin_api.register_plugin_task(AlarmTriggerTaskMock)


class AlarmApiMock():
    def __init__(self, react: ReactBase) -> None:
        self.react = react


    def verify_config(self):
        return self.react.hass.data.get(TEST_FLAG_VERIFY_CONFIG, True)
    

    async def async_alarm_trigger(self, context: Context, entity_id: str):
        tc: TstContext = self.react.hass.data[TEST_CONTEXT]
        tc.register_plugin_data({
            ATTR_ENTITY_ID: entity_id,
        })


class AlarmTriggerTaskMock(AlarmTriggerTask):

    def __init__(self, react: ReactBase) -> None:
        api = AlarmApiMock(react)
        super().__init__(react, api)