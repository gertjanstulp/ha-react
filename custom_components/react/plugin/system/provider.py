from homeassistant.const import (
    ATTR_ENTITY_ID,
    SERVICE_HOMEASSISTANT_RESTART,
)
from homeassistant.core import Context, DOMAIN as HASS_DOMAIN

from custom_components.react.plugin.system.config import SystemConfig
from custom_components.react.plugin.base import PluginProviderBase
from custom_components.react.utils.session import Session


class SystemProvider(PluginProviderBase[SystemConfig]):

    async def async_hass_restart(self, session: Session, context: Context, entity_id: str, state: str):
        await self.plugin.hass_api.async_hass_call_service(
            HASS_DOMAIN,
            SERVICE_HOMEASSISTANT_RESTART,
            context=context,
        )
