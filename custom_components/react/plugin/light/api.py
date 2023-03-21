from homeassistant.components.light import (
    DOMAIN as LIGHT_DOMAIN,
    SERVICE_TURN_ON,
    SERVICE_TURN_OFF,
    SERVICE_TOGGLE,
)
from homeassistant.const import (
    ATTR_ENTITY_ID, 
)
from homeassistant.core import Context

from custom_components.react.base import ReactBase
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData


_LOGGER = get_react_logger()


class ApiConfig(DynamicData):
    def __init__(self, source: DynamicData = None) -> None:
        super().__init__()
        self.load(source)


class Api():
    def __init__(self, react: ReactBase, config: ApiConfig) -> None:
        self.react = react
        self.config = config


    def _debug(self, message: str):
        _LOGGER.debug(f"Light plugin: Api - {message}")


    async def async_light_turn_on(self, context: Context, entity_id: str):
        self._debug(f"Turning on light '{entity_id}'")
        try:
            light_data = {
                ATTR_ENTITY_ID: f"light.{entity_id}",
            }
            await self.react.hass.services.async_call(
                LIGHT_DOMAIN,
                SERVICE_TURN_ON,
                light_data,
                context,
            )
        except:
            _LOGGER.exception("Turning on light failed")


    async def async_light_turn_off(self, context: Context, entity_id: str):
        self._debug(f"Turning off light '{entity_id}'")
        try:
            light_data = {
                ATTR_ENTITY_ID: f"light.{entity_id}",
            }
            await self.react.hass.services.async_call(
                LIGHT_DOMAIN,
                SERVICE_TURN_OFF,
                light_data,
                context,
            )
        except:
            _LOGGER.exception("Turning off light failed")


    async def async_light_toggle(self, context: Context, entity_id: str):
        self._debug(f"Toggling light '{entity_id}'")
        try:
            light_data = {
                ATTR_ENTITY_ID: f"light.{entity_id}",
            }
            await self.react.hass.services.async_call(
                LIGHT_DOMAIN,
                SERVICE_TOGGLE,
                light_data,
                context,
            )
        except:
            _LOGGER.exception("Toggling light failed")
