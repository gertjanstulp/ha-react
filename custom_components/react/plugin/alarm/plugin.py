from custom_components.react.plugin.alarm.api import AlarmApi
from custom_components.react.plugin.alarm.config import AlarmConfig
from custom_components.react.plugin.alarm.const import ALARM_GENERIC_PROVIDER
from custom_components.react.plugin.alarm.provider import AlarmProvider
from custom_components.react.plugin.alarm.tasks.alarm_arm_away_task import AlarmArmAwayTask
from custom_components.react.plugin.alarm.tasks.alarm_arm_home_task import AlarmArmHomeTask
from custom_components.react.plugin.alarm.tasks.alarm_arm_night_task import AlarmArmNightTask
from custom_components.react.plugin.alarm.tasks.alarm_arm_vacation_task import AlarmArmVacationTask
from custom_components.react.plugin.alarm.tasks.alarm_disarm_task import AlarmDisarmTask
from custom_components.react.plugin.alarm.tasks.alarm_trigger_task import AlarmTriggerTask
from custom_components.react.plugin.const import PROVIDER_TYPE_ALARM
from custom_components.react.plugin.plugin_factory import HassApi, PluginApi
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData

_LOGGER = get_react_logger()


def load(plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
    loader = AlarmPluginLoader()
    loader.load(plugin_api, hass_api, config)


class AlarmPluginLoader:
    def load(self, plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
        _LOGGER.debug(f"Alarm plugin: Loading")

        api = AlarmApi(plugin_api, hass_api, AlarmConfig(config))

        plugin_api.register_plugin_provider(
            PROVIDER_TYPE_ALARM, 
            ALARM_GENERIC_PROVIDER,
            AlarmProvider(plugin_api, hass_api))

        plugin_api.register_plugin_task(AlarmArmHomeTask, api=api)
        plugin_api.register_plugin_task(AlarmArmAwayTask, api=api)
        plugin_api.register_plugin_task(AlarmArmNightTask, api=api)
        plugin_api.register_plugin_task(AlarmArmVacationTask, api=api)
        plugin_api.register_plugin_task(AlarmDisarmTask, api=api)
        plugin_api.register_plugin_task(AlarmTriggerTask, api=api)