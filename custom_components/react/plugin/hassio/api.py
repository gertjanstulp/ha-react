from homeassistant.core import Context

from custom_components.react.plugin.const import PROVIDER_TYPE_HASSIO
from custom_components.react.plugin.hassio.config import HassioConfig
from custom_components.react.plugin.hassio.const import HASSIO_GENERIC_PROVIDER
from custom_components.react.plugin.hassio.provider import HassioProvider
from custom_components.react.plugin.base import PluginApiBase
from custom_components.react.utils.session import Session


class HassioApi(PluginApiBase[HassioConfig]):

    async def async_hassio_restart_addon(self, session: Session, context: Context, addon: str, hassio_provider: str = None):
        try:
            session.debug(self.logger, f"Restarting addon {addon}")
            
            provider = self.get_hassio_provider(session, hassio_provider)
            if provider:
                await provider.async_restart_addon(session, context, addon)
        except:
            session.exception(self.logger, "Restarting addon failed")


    def get_hassio_provider(self, session: Session, hassio_provider: str) -> HassioProvider:
        hassio_provider = hassio_provider or self.plugin.config.hassio_provider or HASSIO_GENERIC_PROVIDER
        result = self.plugin.get_provider(PROVIDER_TYPE_HASSIO, hassio_provider)
        if not result:
            session.error(self.plugin.logger, f"Hassio provider for '{hassio_provider}' not found")
            return None
        return result
