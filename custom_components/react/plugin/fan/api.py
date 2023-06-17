from homeassistant.components.fan import (
    ATTR_PERCENTAGE,
)
from homeassistant.const import (
    STATE_OFF,
    STATE_ON
)
from homeassistant.core import Context

from custom_components.react.plugin.const import PROVIDER_TYPE_FAN
from custom_components.react.plugin.fan.config import FanConfig
from custom_components.react.plugin.fan.const import FAN_GENERIC_PROVIDER
from custom_components.react.plugin.fan.provider import FanProvider
from custom_components.react.plugin.base import PluginApiBase
from custom_components.react.utils.session import Session


class FanApi(PluginApiBase[FanConfig]):

    async def async_fan_set_percentage(self, session: Session, context: Context, entity_id: str, fan_provider: str, percentage: int):
        try:
            full_entity_id = f"fan.{entity_id}"
            session.debug(self.logger, f"Setting percentage of fan {full_entity_id} to {percentage}")
            if state := self.plugin.hass_api.hass_get_state(full_entity_id):
                state_value = state.state
                state_percentage = state.attributes.get(ATTR_PERCENTAGE, None)
            else:
                session.warning(self.plugin.logger, f"{full_entity_id} not found")
                return
            
            if provider := self.get_fan_provider(session, fan_provider):
                if ((state_value == STATE_OFF and percentage > 0) or
                    (state_value == STATE_ON and state_percentage != percentage)):
                    await provider.async_set_percentage(session, context, full_entity_id, percentage)
        except:
            session.exception("Setting fan percentage failed")


    async def async_fan_increase_speed(self, session: Session, context: Context, entity_id: str, fan_provider: str, percentage_step: int):
        try:
            full_entity_id = f"fan.{entity_id}"
            session.debug(self.logger, f"Increasing speed of fan '{full_entity_id}'")
            if state := self.plugin.hass_api.hass_get_state(full_entity_id):
                state_value = state.state
                state_percentage = state.attributes.get(ATTR_PERCENTAGE, None)
            else:
                session.warning(self.plugin.logger, f"{full_entity_id} not found")
                return
            
            if provider := self.get_fan_provider(session, fan_provider):
                if state_value == STATE_OFF or state_percentage < 100:
                    await provider.async_increase_speed(session, context, full_entity_id, percentage_step)
        except:
            session.exception("Increasing fan speed failed")
            

    async def async_fan_decrease_speed(self, session: Session, context: Context, entity_id: str, fan_provider: str, percentage_step: int):
        try:
            full_entity_id = f"fan.{entity_id}"
            session.debug(self.logger, f"Decreasing speed of fan  '{full_entity_id}'")
            if state := self.plugin.hass_api.hass_get_state(full_entity_id):
                state_value = state.state
            else:
                session.warning(self.plugin.logger, f"{full_entity_id} not found")
                return
            
            if provider := self.get_fan_provider(session, fan_provider):
                if state_value == STATE_ON:
                    await provider.async_decrease_speed(session, context, full_entity_id, percentage_step)
        except:
            session.exception("Decreasing fan speed failed")


    def get_fan_provider(self, session: Session, fan_provider: str) -> FanProvider:
        fan_provider = fan_provider or self.plugin.config.fan_provider or FAN_GENERIC_PROVIDER
        result = self.plugin.get_provider(PROVIDER_TYPE_FAN, fan_provider)
        if not result:
            session.error(self.plugin.logger, f"Fan provider for '{fan_provider}' not found")
            return None
        return result
