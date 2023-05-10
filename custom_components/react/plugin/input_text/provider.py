from homeassistant.components.input_text import (
    DOMAIN,
    SERVICE_SET_VALUE,
    ATTR_VALUE,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import Context

from custom_components.react.plugin.input_text.config import InputTextConfig
from custom_components.react.plugin.base import PluginProviderBase


class InputTextProvider(PluginProviderBase[InputTextConfig]):

    async def async_input_text_set_value(self, context: Context, entity_id: str, value: str):
        await self.plugin.hass_api.async_hass_call_service(
            DOMAIN,
            SERVICE_SET_VALUE,
            {
                ATTR_ENTITY_ID: entity_id,
                ATTR_VALUE: value,
            },
            context,
        )
