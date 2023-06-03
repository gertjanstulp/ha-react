from homeassistant.components.input_boolean import (
    DOMAIN as BOOLEAN_DOMAIN,
    SERVICE_TURN_ON,
    SERVICE_TURN_OFF,
)
from homeassistant.const import (
    ATTR_ENTITY_ID, 
    STATE_ON,
)
from homeassistant.core import Context

from custom_components.react.plugin.base import PluginProviderBase
from custom_components.react.plugin.input_boolean.config import InputBooleanConfig


class InputBooleanProvider(PluginProviderBase[InputBooleanConfig]):
    
    async def async_input_boolean_set_value(self, context: Context, entity_id: str, value: str):
        await self.plugin.hass_api.async_hass_call_service(
            BOOLEAN_DOMAIN,
            SERVICE_TURN_ON if value == STATE_ON else SERVICE_TURN_OFF,
            {
                ATTR_ENTITY_ID: entity_id,
            },
            context,
        )
