from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import Context
from custom_components.react.const import ATTR_MODE

from custom_components.react.plugin.climate.provider import ClimateProvider
from custom_components.react.plugin.ramses.const import (
    ATTR_SETPOINT, 
    DOMAIN, 
    MODE_ADVANCED_OVERRIDE, 
    SVC_SET_ZONE_MODE,
)
from custom_components.react.utils.session import Session
from custom_components.react.utils.struct import DynamicData


class RamsesProvider(ClimateProvider[DynamicData]):
    async def async_set_temperature(self, session: Session, context: Context, entity_id: str, temperature: float):
        await self.plugin.hass_api.async_hass_call_service(
            DOMAIN,
            SVC_SET_ZONE_MODE,
            {
                ATTR_ENTITY_ID: entity_id,
                ATTR_SETPOINT: temperature,
                ATTR_MODE: MODE_ADVANCED_OVERRIDE,
            },
            context,
        )
