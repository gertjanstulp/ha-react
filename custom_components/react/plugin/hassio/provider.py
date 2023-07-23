from homeassistant.components.hassio.const import DOMAIN, ATTR_ADDON
from homeassistant.components.hassio import SERVICE_ADDON_RESTART
from homeassistant.core import Context

from custom_components.react.plugin.hassio.config import HassioConfig
from custom_components.react.plugin.base import PluginProviderBase
from custom_components.react.utils.session import Session


class HassioProvider(PluginProviderBase[HassioConfig]):

    async def async_restart_addon(self, session: Session, context: Context, addon: str):
        await self.plugin.hass_api.async_hass_call_service(
            DOMAIN,
            SERVICE_ADDON_RESTART,
            service_data={
                ATTR_ADDON: addon,
            },
            context=context,
        )
