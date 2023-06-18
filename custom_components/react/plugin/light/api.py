from homeassistant.const import (
    STATE_OFF,
    STATE_ON
)
from homeassistant.core import Context

from custom_components.react.plugin.const import PROVIDER_TYPE_LIGHT
from custom_components.react.plugin.light.config import LightConfig
from custom_components.react.plugin.light.const import LIGHT_GENERIC_PROVIDER
from custom_components.react.plugin.light.provider import LightProvider
from custom_components.react.plugin.base import PluginApiBase
from custom_components.react.utils.session import Session



class LightApi(PluginApiBase[LightConfig]):

    async def async_light_turn_on(self, session: Session, context: Context, entity_id: str, light_provider: str):
        try:
            full_entity_id = f"light.{entity_id}"
            session.debug(self.logger, f"Turning on {full_entity_id}")
            if state := self.plugin.hass_api.hass_get_state(full_entity_id):
                value = state.state
            else:
                session.warning(self.plugin.logger, f"{full_entity_id} not found")
                return
            
            provider = self.get_light_provider(session, light_provider)
            if provider and value is not None and value == STATE_OFF:
                await provider.async_set_state(session, context, full_entity_id, STATE_ON)
        except:
            session.exception(self.logger, "Turning on light failed")


    async def async_light_turn_off(self, session: Session, context: Context, entity_id: str, light_provider: str):
        try:
            full_entity_id = f"light.{entity_id}"
            session.debug(self.logger, f"Turning off {full_entity_id}")
            if state := self.plugin.hass_api.hass_get_state(full_entity_id):
                value = state.state
            else:
                session.warning(self.plugin.logger, f"{full_entity_id} not found")
                return
            
            provider = self.get_light_provider(session, light_provider)
            if provider and value is not None and value == STATE_ON:
                await provider.async_set_state(session, context, full_entity_id, STATE_OFF)
        except:
            session.exception(self.logger, "Turning off light failed")


    async def async_light_toggle(self, session: Session, context: Context, entity_id: str, light_provider: str):
        try:
            full_entity_id = f"light.{entity_id}"
            session.debug(self.logger, f"Toggling {full_entity_id}")
            if state := self.plugin.hass_api.hass_get_state(full_entity_id):
                value = state.state
            else:
                session.warning(self.plugin.logger, f"{full_entity_id} not found")
                return
            
            provider = self.get_light_provider(session, light_provider)
            if provider and value is not None:
                await provider.async_set_state(session, context, full_entity_id, STATE_ON if value == STATE_OFF else STATE_OFF)
        except:
            session.exception(self.logger, "Toggling light failed")


    def get_light_provider(self, session: Session, light_provider: str) -> LightProvider:
        light_provider = light_provider or self.plugin.config.light_provider or LIGHT_GENERIC_PROVIDER
        result = self.plugin.get_provider(PROVIDER_TYPE_LIGHT, light_provider)
        if not result:
            session.error(self.plugin.logger, f"Light provider for '{light_provider}' not found")
            return None
        return result
