from homeassistant.components.input_boolean import (
    DOMAIN as BOOLEAN_DOMAIN,
    SERVICE_TURN_ON,
    SERVICE_TURN_OFF,
)
from homeassistant.components.input_number import (
    DOMAIN as NUMBER_DOMAIN,
    SERVICE_SET_VALUE as NUMBER_SERVICE_SET_VALUE,
    ATTR_VALUE as NUMBER_ATTR_VALUE,
)
from homeassistant.components.input_text import (
    DOMAIN as TEXT_DOMAIN,
    SERVICE_SET_VALUE as TEXT_SERVICE_SET_VALUE,
    ATTR_VALUE as TEXT_ATTR_VALUE,
)
from homeassistant.const import (
    ATTR_ENTITY_ID, 
    STATE_ON,
)
from homeassistant.core import Context

from custom_components.react.plugin.plugin_factory import HassApi, PluginApi
from custom_components.react.plugin.providers import PluginProvider


class InputProvider(PluginProvider):
    def __init__(self, plugin_api: PluginApi, hass_api: HassApi) -> None:
        super().__init__(plugin_api, hass_api)


    async def async_input_number_set_value(self, context: Context, entity_id: str, value: float):
        await self.hass_api.async_hass_call_service(
            NUMBER_DOMAIN,
            NUMBER_SERVICE_SET_VALUE,
            {
                ATTR_ENTITY_ID: entity_id,
                NUMBER_ATTR_VALUE: value,
            },
            context,
        )


    async def async_input_text_set_value(self, context: Context, entity_id: str, value: str):
        await self.hass_api.async_hass_call_service(
            TEXT_DOMAIN,
            TEXT_SERVICE_SET_VALUE,
            {
                ATTR_ENTITY_ID: entity_id,
                TEXT_ATTR_VALUE: value,
            },
            context,
        )

    
    async def async_input_boolean_set_value(self, context: Context, entity_id: str, value: str):
        await self.hass_api.async_hass_call_service(
            BOOLEAN_DOMAIN,
            SERVICE_TURN_ON if value == STATE_ON else SERVICE_TURN_OFF,
            {
                ATTR_ENTITY_ID: entity_id,
            },
            context,
        )
