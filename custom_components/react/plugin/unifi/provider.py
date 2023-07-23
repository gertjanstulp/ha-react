from homeassistant.components.unifi.const import DOMAIN
from homeassistant.components.unifi.services import SERVICE_RECONNECT_CLIENT
from homeassistant.const import ATTR_DEVICE_ID
from homeassistant.core import Context

from custom_components.react.plugin.unifi.config import UnifiConfig
from custom_components.react.plugin.base import PluginProviderBase
from custom_components.react.utils.session import Session


class UnifiProvider(PluginProviderBase[UnifiConfig]):

    async def async_unifi_set_value(self, session: Session, context: Context, device_id: str):
        await self.plugin.hass_api.async_hass_call_service(
            DOMAIN,
            SERVICE_RECONNECT_CLIENT,
            service_data={
                ATTR_DEVICE_ID: device_id,
            },
            context=context,
        )
