from homeassistant.const import(
    ATTR_ENTITY_ID,
)
from homeassistant.core import Context

from custom_components.react.base import ReactBase
from custom_components.react.const import ATTR_MODE
from custom_components.react.plugin.alarm.api import Api, ApiConfig
from custom_components.react.plugin.alarm.const import ArmMode
from custom_components.react.plugin.alarm.service import Service
from custom_components.react.plugin.alarm.tasks.alarm_arm_away_task import AlarmArmAwayTask
from custom_components.react.plugin.alarm.tasks.alarm_arm_home_task import AlarmArmHomeTask
from custom_components.react.plugin.alarm.tasks.alarm_arm_night_task import AlarmArmNightTask
from custom_components.react.plugin.alarm.tasks.alarm_arm_vacation_task import AlarmArmVacationTask
from custom_components.react.plugin.alarm.tasks.alarm_disarm_task import AlarmDisarmTask
from custom_components.react.plugin.alarm.tasks.alarm_trigger_task import AlarmTriggerTask
from custom_components.react.plugin.plugin_factory import PluginApi
from custom_components.react.utils.struct import DynamicData
from tests.common import TEST_CONTEXT, TEST_FLAG_VERIFY_CONFIG
from tests.tst_context import TstContext


def load(plugin_api: PluginApi, config: DynamicData):
    api = AlarmApiMock(plugin_api.react, ApiConfig(config))
    plugin_api.register_plugin_task(AlarmArmHomeTask, api=api)
    plugin_api.register_plugin_task(AlarmArmAwayTask, api=api)
    plugin_api.register_plugin_task(AlarmArmNightTask, api=api)
    plugin_api.register_plugin_task(AlarmArmVacationTask, api=api)
    plugin_api.register_plugin_task(AlarmDisarmTask, api=api)
    plugin_api.register_plugin_task(AlarmTriggerTask, api=api)


class AlarmApiMock(Api):
    def __init__(self, react: ReactBase, config: ApiConfig) -> None:
        super().__init__(react, config, AlarmServiceMock(react))


    def verify_config(self):
        return self.react.hass.data.get(TEST_FLAG_VERIFY_CONFIG, True)
    

class AlarmServiceMock(Service):
    def __init__(self, react: ReactBase) -> None:
        self.react = react


    async def async_arm(self, context: Context, entity_id: str, code: str, arm_mode: ArmMode):
        await super().async_arm(context, entity_id, code, arm_mode)
        tc: TstContext = self.react.hass.data[TEST_CONTEXT]
        tc.register_plugin_data({
            ATTR_ENTITY_ID: entity_id,
            ATTR_MODE: arm_mode,
        })

    
    async def async_disarm(self, context: Context, entity_id: str, code: str):
        await super().async_disarm(context, entity_id, code)
        tc: TstContext = self.react.hass.data[TEST_CONTEXT]
        tc.register_plugin_data({
            ATTR_ENTITY_ID: entity_id,
        })


    async def async_trigger(self, context: Context, entity_id: str):
        await super().async_trigger(context, entity_id)
        tc: TstContext = self.react.hass.data[TEST_CONTEXT]
        tc.register_plugin_data({
            ATTR_ENTITY_ID: entity_id,
        })
