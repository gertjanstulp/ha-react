from datetime import datetime
from typing import Any

from homeassistant.core import Context

from custom_components.react.plugin.const import PROVIDER_TYPE_STATE
from custom_components.react.plugin.state.config import StateConfig
from custom_components.react.plugin.state.const import STATE_GENERIC_PROVIDER
from custom_components.react.plugin.state.provider import StateProvider
from custom_components.react.plugin.base import PluginApiBase
from custom_components.react.utils.session import Session


class StateApi(PluginApiBase[StateConfig]):

    async def async_track_entity_state_change(self, 
        session: Session,
        context: Context, 
        entity_id: str, 
        old_state: Any, 
        new_state: Any, 
        timestamp: datetime,
        state_provider: str = None
    ):
        session.debug(self.logger, f"Tracking state of entity '{entity_id}' ('{str(old_state)}' -> '{str(new_state)}')")
        try:
            if not self.plugin.hass_api.hass_get_state(entity_id):
                session.warning(self.plugin.logger, f"{entity_id} not found")
                return
            
            provider = self.get_state_provider(session, state_provider)
            if provider:
                await provider.async_track_entity_state_change(session, context, entity_id, old_state, new_state, timestamp)
        except:
            self.plugin.logger.exception("Tracking state of entity '{entity_id}' failed")


    def get_state_provider(self, session: Session, state_provider: str) -> StateProvider:
        state_provider = state_provider or self.plugin.config.state_provider or STATE_GENERIC_PROVIDER
        result = self.plugin.get_provider(PROVIDER_TYPE_STATE, state_provider)
        if not result:
            session.error(self.plugin.logger, f"State provider for '{state_provider}' not found")
            return None
        return result
