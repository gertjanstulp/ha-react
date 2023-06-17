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
from custom_components.react.utils.session import Session


ARMED_STATES = [
    STATE_ALARM_ARMED_HOME,
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_ARMED_NIGHT,
    STATE_ALARM_ARMED_VACATION, 
    STATE_ALARM_ARMING,
    STATE_ALARM_PENDING,
    STATE_ALARM_TRIGGERED,
]

class AlarmApi(PluginApiBase[AlarmConfig]):

    async def _async_alarm_arm(self, session: Session, context: Context, entity_id: str, arm_mode: ArmMode, alarm_control_panel_provider: str):
        try:
            full_entity_id = f"alarm_control_panel.{entity_id}"
            session.debug(self.logger, f"Arming {arm_mode} {full_entity_id}")
            if state := self.plugin.hass_api.hass_get_state(full_entity_id):
                value = state.state
            else:
                session.warning(self.plugin.logger, f"{full_entity_id} not found")
                return
            
            provider = self.get_alarm_control_panel_provider(session, alarm_control_panel_provider)
            if provider and value is not None and value == STATE_ALARM_DISARMED:
                await provider.async_arm(session, context, full_entity_id, self.plugin.config.code, arm_mode)
        except:
            session.exception(f"Arming {arm_mode} failed")


    async def async_alarm_arm_home(self, session: Session, context: Context, entity_id: str, alarm_control_panel_provider: str):
        await self._async_alarm_arm(session, context, entity_id, ArmMode.HOME, alarm_control_panel_provider)


    async def async_alarm_arm_away(self, session: Session, context: Context, entity_id: str, alarm_control_panel_provider: str):
        await self._async_alarm_arm(session, context, entity_id, ArmMode.AWAY, alarm_control_panel_provider)


    async def async_alarm_arm_night(self, session: Session, context: Context, entity_id: str, alarm_control_panel_provider: str):
        await self._async_alarm_arm(session, context, entity_id, ArmMode.NIGHT, alarm_control_panel_provider)


    async def async_alarm_arm_vacation(self, session: Session, context: Context, entity_id: str, alarm_control_panel_provider: str):
        await self._async_alarm_arm(session, context, entity_id, ArmMode.VACATION, alarm_control_panel_provider)


    async def async_alarm_disarm(self, session: Session, context: Context, entity_id: str, alarm_control_panel_provider: str):
        try:
            full_entity_id = f"alarm_control_panel.{entity_id}"
            session.debug(self.logger, f"Disarming {full_entity_id}")
            if state := self.plugin.hass_api.hass_get_state(full_entity_id):
                value = state.state
            else:
                session.warning(self.plugin.logger, f"{full_entity_id} not found")
                return

            provider = self.get_alarm_control_panel_provider(session, alarm_control_panel_provider)
            if provider and value is not None and value in ARMED_STATES:
                await provider.async_disarm(session, context, full_entity_id, self.plugin.config.code)
        except:
            session.exception("Disarming failed")


    async def async_alarm_trigger(self, session: Session, context: Context, entity_id: str, alarm_control_panel_provider: str):
        try:
            full_entity_id = f"alarm_control_panel.{entity_id}"
            session.debug(self.logger, f"Triggering alarm {full_entity_id}")
            if state := self.plugin.hass_api.hass_get_state(full_entity_id):
                value = state.state
            else:
                session.warning(self.plugin.logger, f"{full_entity_id} not found")
                return

            provider = self.get_alarm_control_panel_provider(session, alarm_control_panel_provider)
            if provider and value is not None and value in ARMED_STATES:
                await provider.async_trigger(session, context, full_entity_id)
        except:
            session.exception("Triggering alarm failed")


    def get_alarm_control_panel_provider(self, session: Session, alarm_control_panel_provider: str) -> AlarmProvider:
        alarm_control_panel_provider = alarm_control_panel_provider or self.plugin.config.alarm_control_panel_provider or ALARM_GENERIC_PROVIDER
        result = self.plugin.get_provider(PROVIDER_TYPE_ALARM_CONTROL_PANEL, alarm_control_panel_provider)
        if not result:
            session.error(self.plugin.logger, f"Alarm_control_panel provider for '{alarm_control_panel_provider}' not found")
            return None
        return result