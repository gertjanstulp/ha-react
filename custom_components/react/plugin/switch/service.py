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

from custom_components.react.base import ReactBase


class SwitchService():
    def __init__(self, react: ReactBase) -> None:
        self.react = react


    async def async_set_state(self, context: Context, entity_id: str, state: str):
        await self.react.hass.services.async_call(
            SWITCH_DOMAIN,
            SERVICE_TURN_ON if state == STATE_ON else SERVICE_TURN_OFF,
            {
                ATTR_ENTITY_ID: entity_id,
            },
            context,
        )