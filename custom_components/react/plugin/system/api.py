from homeassistant.const import (
    STATE_OFF,
    STATE_ON
)
from homeassistant.core import Context

from custom_components.react.plugin.const import PROVIDER_TYPE_SYSTEM
from custom_components.react.plugin.base import PluginApiBase
from custom_components.react.plugin.system.config import SystemConfig
from custom_components.react.plugin.system.const import SYSTEM_GENERIC_PROVIDER
from custom_components.react.plugin.system.provider import SystemProvider
from custom_components.react.utils.session import Session


class SystemApi(PluginApiBase[SystemConfig]):

    async def async_system_restart(self, session: Session, context: Context, system_provider: str):
        try:
            session.debug(self.logger, f"Shutting down HomeAssistant")
            provider = self.get_system_provider(session, system_provider)
            if provider:
                await provider.async_hass_restart(session, context)
        except:
            session.exception(self.logger, "Shutting down system failed")


    def get_system_provider(self, session: Session, system_provider: str) -> SystemProvider:
        system_provider = system_provider or self.plugin.config.system_provider or SYSTEM_GENERIC_PROVIDER
        result = self.plugin.get_provider(PROVIDER_TYPE_SYSTEM, system_provider)
        if not result:
            session.error(self.plugin.logger, f"System provider for '{system_provider}' not found")
            return None
        return result
