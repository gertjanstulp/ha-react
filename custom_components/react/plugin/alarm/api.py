from homeassistant.const import (
    STATE_ALARM_ARMED_HOME,
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_ARMED_NIGHT,
    STATE_ALARM_ARMED_VACATION,
    STATE_ALARM_DISARMED
)
from homeassistant.core import Context

from custom_components.react.base import ReactBase
from custom_components.react.plugin.alarm.const import ArmMode
from custom_components.react.plugin.alarm.service import AlarmService
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData


_LOGGER = get_react_logger()

ARMED_STATES = [STATE_ALARM_ARMED_HOME, STATE_ALARM_ARMED_AWAY, STATE_ALARM_ARMED_NIGHT, STATE_ALARM_ARMED_VACATION]


class AlarmApiConfig(DynamicData):
    def __init__(self, source: DynamicData = None) -> None:
        super().__init__()
        self.code: str = None
        self.load(source)


class AlarmApi():
    def __init__(self, react: ReactBase, config: AlarmApiConfig, service: AlarmService) -> None:
        self.react = react
        self.config = config
        self.service = service


    def _debug(self, message: str):
        _LOGGER.debug(f"Alarm plugin: Api - {message}")


    def verify_config(self) -> bool:
        if not self.config.code:
            _LOGGER.error("Alarm - No code configured")
            return False
        return True


    async def _async_alarm_arm(self, context: Context, entity_id: str, mode: ArmMode):
        self._debug(f"Arming {mode} '{entity_id}'")
        try:
            full_entity_id = f"alarm_control_panel.{entity_id}"
            if state := self.react.hass.states.get(full_entity_id):
                value = state.state
            else:
                _LOGGER.warn(f"Alarm plugin: Api - {full_entity_id} not found")

            if value is not None and value == STATE_ALARM_DISARMED:
                await self.service.async_arm(context, full_entity_id, self.config.code, mode)
        except:
            _LOGGER.exception(f"Arming {mode} failed")

    async def async_alarm_arm_home(self, context: Context, entity_id: str):
        await self._async_alarm_arm(context, entity_id, ArmMode.HOME)


    async def async_alarm_arm_away(self, context: Context, entity_id: str):
        await self._async_alarm_arm(context, entity_id, ArmMode.AWAY)


    async def async_alarm_arm_night(self, context: Context, entity_id: str):
        await self._async_alarm_arm(context, entity_id, ArmMode.NIGHT)


    async def async_alarm_arm_vacation(self, context: Context, entity_id: str):
        await self._async_alarm_arm(context, entity_id, ArmMode.VACATION)


    async def async_alarm_disarm(self, context: Context, entity_id: str):
        self._debug(f"Disarming '{entity_id}'")
        try:
            full_entity_id = f"alarm_control_panel.{entity_id}"
            if state := self.react.hass.states.get(full_entity_id):
                value = state.state
            else:
                _LOGGER.warn(f"Alarm plugin: Api - {full_entity_id} not found")

            if value is not None and value in ARMED_STATES:
                await self.service.async_disarm(context, full_entity_id, self.config.code)
        except:
            _LOGGER.exception("Disarming failed")


    async def async_alarm_trigger(self, context: Context, entity_id: str):
        self._debug(f"Triggering '{entity_id}'")
        try:
            full_entity_id = f"alarm_control_panel.{entity_id}"
            if state := self.react.hass.states.get(full_entity_id):
                value = state.state
            else:
                _LOGGER.warn(f"Alarm plugin: Api - {full_entity_id} not found")

            if value is not None and value in ARMED_STATES:
                await self.service.async_trigger(context, full_entity_id)
        except:
            _LOGGER.exception("Triggering failed")