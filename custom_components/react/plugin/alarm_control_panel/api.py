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
from custom_components.react.plugin.alarm_control_panel.config import AlarmConfig

from custom_components.react.plugin.alarm_control_panel.const import ALARM_GENERIC_PROVIDER, ArmMode
from custom_components.react.plugin.alarm_control_panel.provider import AlarmProvider
from custom_components.react.plugin.const import PROVIDER_TYPE_ALARM_CONTROL_PANEL
from custom_components.react.plugin.base import PluginApiBase
from custom_components.react.utils.logger import get_react_logger



ARMED_STATES = [
    STATE_ALARM_ARMED_HOME,
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_ARMED_NIGHT,
    STATE_ALARM_ARMED_VACATION, 
    STATE_ALARM_ARMING,
    STATE_ALARM_PENDING,
    STATE_ALARM_TRIGGERED,
]

_LOGGER = get_react_logger()

class AlarmApi(PluginApiBase[AlarmConfig]):

    def _debug(self, message: str):
        _LOGGER.debug(f"Alarm_control_panel plugin: Api - {message}")       


    async def _async_alarm_arm(self, context: Context, entity_id: str, arm_mode: ArmMode, alarm_control_panel_provider: str):
        self._debug(f"Arming {arm_mode} '{entity_id}'")
        try:
            full_entity_id = f"alarm_control_panel.{entity_id}"
            if state := self.plugin.hass_api.hass_get_state(full_entity_id):
                value = state.state
            else:
                _LOGGER.warn(f"Alarm_control_panel plugin: Api - {full_entity_id} not found")
                return
            
            provider = self.get_alarm_control_panel_provider(alarm_control_panel_provider)
            if provider and value is not None and value == STATE_ALARM_DISARMED:
                await provider.async_arm(context, full_entity_id, self.plugin.config.code, arm_mode)
        except:
            _LOGGER.exception(f"Arming {arm_mode} failed")


    async def async_alarm_arm_home(self, context: Context, entity_id: str, alarm_control_panel_provider: str):
        await self._async_alarm_arm(context, entity_id, ArmMode.HOME, alarm_control_panel_provider)


    async def async_alarm_arm_away(self, context: Context, entity_id: str, alarm_control_panel_provider: str):
        await self._async_alarm_arm(context, entity_id, ArmMode.AWAY, alarm_control_panel_provider)


    async def async_alarm_arm_night(self, context: Context, entity_id: str, alarm_control_panel_provider: str):
        await self._async_alarm_arm(context, entity_id, ArmMode.NIGHT, alarm_control_panel_provider)


    async def async_alarm_arm_vacation(self, context: Context, entity_id: str, alarm_control_panel_provider: str):
        await self._async_alarm_arm(context, entity_id, ArmMode.VACATION, alarm_control_panel_provider)


    async def async_alarm_disarm(self, context: Context, entity_id: str, alarm_control_panel_provider: str):
        self._debug(f"Disarming '{entity_id}'")
        try:
            full_entity_id = f"alarm_control_panel.{entity_id}"
            if state := self.plugin.hass_api.hass_get_state(full_entity_id):
                value = state.state
            else:
                _LOGGER.warn(f"Alarm_control_panel plugin: Api - {full_entity_id} not found")
                return

            provider = self.get_alarm_control_panel_provider(alarm_control_panel_provider)
            if provider and value is not None and value in ARMED_STATES:
                await provider.async_disarm(context, full_entity_id, self.plugin.config.code)
        except:
            _LOGGER.exception("Disarming failed")


    async def async_alarm_trigger(self, context: Context, entity_id: str, alarm_control_panel_provider: str):
        self._debug(f"Triggering '{entity_id}'")
        try:
            full_entity_id = f"alarm_control_panel.{entity_id}"
            if state := self.plugin.hass_api.hass_get_state(full_entity_id):
                value = state.state
            else:
                _LOGGER.warn(f"Alarm_control_panel plugin: Api - {full_entity_id} not found")
                return

            provider = self.get_alarm_control_panel_provider(alarm_control_panel_provider)
            if provider and value is not None and value in ARMED_STATES:
                await provider.async_trigger(context, full_entity_id)
        except:
            _LOGGER.exception("Triggering failed")


    def get_alarm_control_panel_provider(self, alarm_control_panel_provider: str) -> AlarmProvider:
        alarm_control_panel_provider = alarm_control_panel_provider or self.plugin.config.alarm_control_panel_provider or ALARM_GENERIC_PROVIDER
        result = self.plugin.get_provider(PROVIDER_TYPE_ALARM_CONTROL_PANEL, alarm_control_panel_provider)
        if not result:
            _LOGGER.error(f"Alarm_control_panel plugin: Api - Alarm_control_panel provider for '{alarm_control_panel_provider}' not found")
            return None
        return result