from typing import Generic, TypeVar

from homeassistant.components.climate import (
    SERVICE_SET_TEMPERATURE,
)
from homeassistant.components.climate.const import (
    DOMAIN as CLIMATE_DOMAIN,
)
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_TEMPERATURE,
)
from homeassistant.core import Context

from custom_components.react.plugin.base import PluginProviderBase
from custom_components.react.utils.session import Session
from custom_components.react.utils.struct import DynamicData

T_config = TypeVar("T_config", bound=DynamicData)


class ClimateProvider(Generic[T_config], PluginProviderBase[T_config]):

    async def async_set_temperature(self, session: Session, context: Context, entity_id: str, temperature: float):
        await self.plugin.hass_api.async_hass_call_service(
            CLIMATE_DOMAIN,
            SERVICE_SET_TEMPERATURE,
            {
                ATTR_ENTITY_ID: entity_id,
                ATTR_TEMPERATURE: temperature,
            }, 
            context
        )
