from homeassistant.const import (
    STATE_ALARM_ARMED_HOME,
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_ARMED_NIGHT,
    STATE_ALARM_ARMED_VACATION,
    STATE_ALARM_DISARMED,
    STATE_ALARM_ARMING,
    STATE_ALARM_PENDING,
    STATE_ALARM_TRIGGERED,
)
from homeassistant.core import Context
from custom_components.react.plugin.alarm.config import AlarmConfig

from custom_components.react.plugin.alarm.const import ALARM_GENERIC_PROVIDER, ArmMode
from custom_components.react.plugin.alarm.provider import AlarmProvider
from custom_components.react.plugin.const import PROVIDER_TYPE_ALARM
from custom_components.react.plugin.plugin_factory import ApiBase, HassApi, PluginApi
from custom_components.react.utils.logger import get_react_logger


_LOGGER = get_react_logger()

ARMED_STATES = [
    STATE_ALARM_ARMED_HOME,
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_ARMED_NIGHT,
    STATE_ALARM_ARMED_VACATION, 
    STATE_ALARM_ARMING,
    STATE_ALARM_PENDING,
    STATE_ALARM_TRIGGERED,
]


class AlarmApi(ApiBase):
    def __init__(self, plugin_api: PluginApi, hass_api: HassApi, config: AlarmConfig) -> None:
        super().__init__(plugin_api, hass_api)
        self.config = config


    def _debug(self, message: str):
        _LOGGER.debug(f"Alarm plugin: Api - {message}")


    def verify_config(self) -> bool:
        if not self.config.code:
            _LOGGER.error("Alarm plugin: Api - No code configured")
            return False
        return True


    async def _async_alarm_arm(self, context: Context, entity_id: str, arm_mode: ArmMode, alarm_provider_name: str):
        self._debug(f"Arming {arm_mode} '{entity_id}'")
        try:
            full_entity_id = f"alarm_control_panel.{entity_id}"
            if state := self.hass_api.hass_get_state(full_entity_id):
                value = state.state
            else:
                _LOGGER.warn(f"Alarm plugin: Api - {full_entity_id} not found")
                return
            
            alarm_provider = self.get_alarm_provider(alarm_provider_name)
            if alarm_provider and value is not None and value == STATE_ALARM_DISARMED:
                await alarm_provider.async_arm(context, full_entity_id, self.config.code, arm_mode)
        except:
            _LOGGER.exception(f"Arming {arm_mode} failed")


    async def async_alarm_arm_home(self, context: Context, entity_id: str, alarm_provider_name: str):
        await self._async_alarm_arm(context, entity_id, ArmMode.HOME, alarm_provider_name)


    async def async_alarm_arm_away(self, context: Context, entity_id: str, alarm_provider_name: str):
        await self._async_alarm_arm(context, entity_id, ArmMode.AWAY, alarm_provider_name)


    async def async_alarm_arm_night(self, context: Context, entity_id: str, alarm_provider_name: str):
        await self._async_alarm_arm(context, entity_id, ArmMode.NIGHT, alarm_provider_name)


    async def async_alarm_arm_vacation(self, context: Context, entity_id: str, alarm_provider_name: str):
        await self._async_alarm_arm(context, entity_id, ArmMode.VACATION, alarm_provider_name)


    async def async_alarm_disarm(self, context: Context, entity_id: str, alarm_provider_name: str):
        self._debug(f"Disarming '{entity_id}'")
        try:
            full_entity_id = f"alarm_control_panel.{entity_id}"
            if state := self.hass_api.hass_get_state(full_entity_id):
                value = state.state
            else:
                _LOGGER.warn(f"Alarm plugin: Api - {full_entity_id} not found")
                return

            alarm_provider = self.get_alarm_provider(alarm_provider_name)
            if alarm_provider and value is not None and value in ARMED_STATES:
                await alarm_provider.async_disarm(context, full_entity_id, self.config.code)
        except:
            _LOGGER.exception("Disarming failed")


    async def async_alarm_trigger(self, context: Context, entity_id: str, alarm_provider_name: str):
        self._debug(f"Triggering '{entity_id}'")
        try:
            full_entity_id = f"alarm_control_panel.{entity_id}"
            if state := self.hass_api.hass_get_state(full_entity_id):
                value = state.state
            else:
                _LOGGER.warn(f"Alarm plugin: Api - {full_entity_id} not found")
                return

            alarm_provider = self.get_alarm_provider(alarm_provider_name)
            if alarm_provider and value is not None and value in ARMED_STATES:
                await alarm_provider.async_trigger(context, full_entity_id)
        except:
            _LOGGER.exception("Triggering failed")


    def get_alarm_provider(self, alarm_provider_name: str) -> AlarmProvider:
        alarm_provider_name = alarm_provider_name or self.config.alarm_provider_name or ALARM_GENERIC_PROVIDER
        result = self.plugin_api.get_provider(PROVIDER_TYPE_ALARM, alarm_provider_name)
        if not result:
            _LOGGER.error(f"Alarm plugin: Api - Alarm provider for '{alarm_provider_name}' not found")
            return None
        return result