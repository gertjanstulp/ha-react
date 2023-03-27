from custom_components.react.plugin.alarm.service import AlarmService
from custom_components.react.plugin.alarm.tasks.alarm_arm_away_task import AlarmArmAwayTask
from custom_components.react.plugin.alarm.tasks.alarm_arm_home_task import AlarmArmHomeTask
from custom_components.react.plugin.alarm.tasks.alarm_arm_night_task import AlarmArmNightTask
from custom_components.react.plugin.alarm.tasks.alarm_arm_vacation_task import AlarmArmVacationTask
from custom_components.react.plugin.alarm.tasks.alarm_disarm_task import AlarmDisarmTask
from custom_components.react.plugin.alarm.tasks.alarm_trigger_task import AlarmTriggerTask
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData

from custom_components.react.plugin.plugin_factory import PluginApi
from custom_components.react.plugin.alarm.api import AlarmApi, AlarmApiConfig

_LOGGER = get_react_logger()

def load(plugin_api: PluginApi, config: DynamicData):
    _LOGGER.debug(f"Alarm plugin: Loading")

    api = AlarmApi(plugin_api.react, AlarmApiConfig(config), AlarmService(plugin_api.react))

    plugin_api.register_plugin_task(AlarmArmHomeTask, api=api)
    plugin_api.register_plugin_task(AlarmArmAwayTask, api=api)
    plugin_api.register_plugin_task(AlarmArmNightTask, api=api)
    plugin_api.register_plugin_task(AlarmArmVacationTask, api=api)
    plugin_api.register_plugin_task(AlarmDisarmTask, api=api)
    plugin_api.register_plugin_task(AlarmTriggerTask, api=api)