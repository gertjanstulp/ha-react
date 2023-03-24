from homeassistant.components.light import (
    DOMAIN as LIGHT_DOMAIN,
    SERVICE_TURN_ON,
    SERVICE_TURN_OFF,
    SERVICE_TOGGLE,
)
from homeassistant.const import (
    ATTR_ENTITY_ID,
    STATE_ON
)
from homeassistant.core import Context

from custom_components.react.base import ReactBase


class Service():
    def __init__(self, react: ReactBase) -> None:
        self.react = react


    async def async_set_state(self, context: Context, entity_id: str, state: str):
        await self.react.hass.services.async_call(
            LIGHT_DOMAIN,
            SERVICE_TURN_ON if state == STATE_ON else SERVICE_TURN_OFF,
            {
                ATTR_ENTITY_ID: entity_id,
            },
            context,
        )