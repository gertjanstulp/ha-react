from homeassistant.components.fan import (
    ATTR_PERCENTAGE,
    ATTR_PERCENTAGE_STEP,
    DOMAIN as FAN_DOMAIN,
    SERVICE_SET_PERCENTAGE,
    SERVICE_INCREASE_SPEED,
    SERVICE_DECREASE_SPEED,
)
from homeassistant.const import (
    ATTR_ENTITY_ID,
    STATE_ON
)
from homeassistant.core import Context

from custom_components.react.plugin.fan.config import FanConfig
from custom_components.react.plugin.base import PluginProviderBase
from custom_components.react.utils.session import Session


class FanProvider(PluginProviderBase[FanConfig]):

    async def async_set_percentage(self, session: Session, context: Context, entity_id: str, percentage: int):
        await self.plugin.hass_api.async_hass_call_service(
            FAN_DOMAIN,
            SERVICE_SET_PERCENTAGE,
            service_data={
                ATTR_ENTITY_ID: entity_id,
                ATTR_PERCENTAGE: percentage
            },
            context=context,
        )


    async def async_increase_speed(self, session: Session, context: Context, entity_id: str, percentage_step: int = None):
        data = {
            ATTR_ENTITY_ID: entity_id
        }
        if percentage_step:
            data[ATTR_PERCENTAGE_STEP] = percentage_step
        await self.plugin.hass_api.async_hass_call_service(
            FAN_DOMAIN,
            SERVICE_INCREASE_SPEED,
            service_data=data,
            context=context,
        )


    async def async_decrease_speed(self, session: Session, context: Context, entity_id: str, percentage_step: int = None):
        data = {
            ATTR_ENTITY_ID: entity_id
        }
        if percentage_step:
            data[ATTR_PERCENTAGE_STEP] = percentage_step
        await self.plugin.hass_api.async_hass_call_service(
            FAN_DOMAIN,
            SERVICE_DECREASE_SPEED,
            service_data=data,
            context=context,
        )