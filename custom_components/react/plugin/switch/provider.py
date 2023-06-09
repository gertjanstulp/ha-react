from homeassistant.components.switch import (
    DOMAIN as SWITCH_DOMAIN,
    SERVICE_TURN_ON,
    SERVICE_TURN_OFF,
)
from homeassistant.const import (
    ATTR_ENTITY_ID,
    STATE_ON
)
from homeassistant.core import Context

from custom_components.react.plugin.base import PluginProviderBase
from custom_components.react.plugin.switch.config import SwitchConfig
from custom_components.react.utils.session import Session


class SwitchProvider(PluginProviderBase[SwitchConfig]):

    async def async_set_state(self, session: Session, context: Context, entity_id: str, state: str):
        await self.plugin.hass_api.async_hass_call_service(
            SWITCH_DOMAIN,
            SERVICE_TURN_ON if state == STATE_ON else SERVICE_TURN_OFF,
            {
                ATTR_ENTITY_ID: entity_id,
            },
            context,
        )
