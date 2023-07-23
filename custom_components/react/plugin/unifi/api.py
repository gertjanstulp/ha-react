from homeassistant.core import Context

from custom_components.react.plugin.const import PROVIDER_TYPE_UNIFI
from custom_components.react.plugin.unifi.config import UnifiConfig
from custom_components.react.plugin.unifi.const import UNIFI_GENERIC_PROVIDER
from custom_components.react.plugin.unifi.provider import UnifiProvider
from custom_components.react.plugin.base import PluginApiBase
from custom_components.react.utils.session import Session


class UnifiApi(PluginApiBase[UnifiConfig]):

    async def async_unifi_reconnect_client(self, session: Session, context: Context, device_id: str, unifi_provider: str = None):
        try:
            session.debug(self.logger, f"Reconnecting client with device_id {device_id}")
            if device := self.plugin.hass_api.hass_get_device(device_id):
                if device.disabled:
                    session.warning(self.plugin.logger, f"Device with device_id {device_id} is disabled")
                    return    
            else:
                session.warning(self.plugin.logger, f"Device with device_id {device_id} not found")
                return
            
            provider = self.get_unifi_provider(session, unifi_provider)
            if provider:
                await provider.async_reconnect_client(session, context, device_id)
        except:
            session.exception(self.logger, "Reconnection client failed")


    def get_unifi_provider(self, session: Session, unifi_provider: str) -> UnifiProvider:
        unifi_provider = unifi_provider or self.plugin.config.unifi_provider or UNIFI_GENERIC_PROVIDER
        result = self.plugin.get_provider(PROVIDER_TYPE_UNIFI, unifi_provider)
        if not result:
            session.error(self.plugin.logger, f"Unifi provider for '{unifi_provider}' not found")
            return None
        return result
