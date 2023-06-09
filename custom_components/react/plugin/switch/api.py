from homeassistant.const import (
    STATE_OFF,
    STATE_ON
)
from homeassistant.core import Context

from custom_components.react.plugin.const import PROVIDER_TYPE_SWITCH
from custom_components.react.plugin.base import PluginApiBase
from custom_components.react.plugin.switch.config import SwitchConfig
from custom_components.react.plugin.switch.const import SWITCH_GENERIC_PROVIDER
from custom_components.react.plugin.switch.provider import SwitchProvider
from custom_components.react.utils.session import Session


class SwitchApi(PluginApiBase[SwitchConfig]):

    async def async_switch_turn_on(self, session: Session, context: Context, entity_id: str, switch_provider: str):
        session.debug(self.logger, f"Turning on switch '{entity_id}'")
        try:
            full_entity_id = f"switch.{entity_id}"
            if state := self.plugin.hass_api.hass_get_state(full_entity_id):
                value = state.state
            else:
                session.warning(self.plugin.logger, f"{full_entity_id} not found")
                return
            
            provider = self.get_switch_provider(session, switch_provider)
            if provider and value is not None and value == STATE_OFF:
                await provider.async_set_state(session, context, full_entity_id, STATE_ON)
        except:
            self.plugin.logger.exception("Turning on switch failed")


    async def async_switch_turn_off(self, session: Session, context: Context, entity_id: str, switch_provider: str):
        session.debug(self.logger, f"Turning off switch '{entity_id}'")
        try:
            full_entity_id = f"switch.{entity_id}"
            if state := self.plugin.hass_api.hass_get_state(full_entity_id):
                value = state.state
            else:
                session.warning(self.plugin.logger, f"{full_entity_id} not found")
                return
            
            provider = self.get_switch_provider(session, switch_provider)
            if provider and value is not None and value == STATE_ON:
                await provider.async_set_state(session, context, full_entity_id, STATE_OFF)
        except:
            self.plugin.logger.exception("Turning off switch failed")


    async def async_switch_toggle(self, session: Session, context: Context, entity_id: str, switch_provider: str):
        session.debug(self.logger, f"Toggling switch '{entity_id}'")
        try:
            full_entity_id = f"switch.{entity_id}"
            if state := self.plugin.hass_api.hass_get_state(full_entity_id):
                value = state.state
            else:
                session.warning(self.plugin.logger, f"{full_entity_id} not found")
                return
            
            provider = self.get_switch_provider(session, switch_provider)
            if provider and value is not None:
                await provider.async_set_state(session, context, full_entity_id, STATE_ON if value == STATE_OFF else STATE_OFF)
        except:
            self.plugin.logger.exception("Toggling switch failed")


    def get_switch_provider(self, session: Session, switch_provider: str) -> SwitchProvider:
        switch_provider = switch_provider or self.plugin.config.switch_provider or SWITCH_GENERIC_PROVIDER
        result = self.plugin.get_provider(PROVIDER_TYPE_SWITCH, switch_provider)
        if not result:
            session.error(self.plugin.logger, f"Switch provider for '{switch_provider}' not found")
            return None
        return result

