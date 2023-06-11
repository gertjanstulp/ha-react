from datetime import datetime
from typing import Any

from homeassistant.core import Context
from homeassistant.util import dt as dt_util

from custom_components.react.plugin.base import PluginProviderBase
from custom_components.react.utils.session import Session
from custom_components.react.utils.struct import StateConfig

class StateProvider(PluginProviderBase[StateConfig]):

    async def async_track_entity_state_change(self, session: Session, context: Context, entity_id: str, old_state: Any, new_state: Any, timestamp: datetime):
        self.plugin.logger.info(f"{timestamp.astimezone(dt_util.DEFAULT_TIME_ZONE)}|{entity_id}|{old_state}|{new_state}")