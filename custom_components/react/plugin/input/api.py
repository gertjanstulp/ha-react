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
from homeassistant.components.input_boolean import (
    DOMAIN as BOOLEAN_DOMAIN,
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
        _LOGGER.debug(f"Input plugin: Api - {message}")


    async def async_input_number_set(self, context: Context, entity_id: str, value: float):
        self._debug(f"Setting input_number '{entity_id}' to '{str(value)}'")
        try:
            input_number_data = {
                ATTR_ENTITY_ID: f"input_number.{entity_id}",
                NUMBER_ATTR_VALUE: value,
            }
            await self.react.hass.services.async_call(
                NUMBER_DOMAIN,
                NUMBER_SERVICE_SET_VALUE,
                input_number_data,
                context,
            )
        except:
            _LOGGER.exception("Setting input_number failed")


    async def async_input_text_set(self, context: Context, entity_id: str, value: str):
        self._debug(f"Setting input_text '{entity_id}' to '{str(value)}'")
        try:
            input_text_data = {
                ATTR_ENTITY_ID: f"input_text.{entity_id}",
                TEXT_ATTR_VALUE: value,
            }
            await self.react.hass.services.async_call(
                TEXT_DOMAIN,
                TEXT_SERVICE_SET_VALUE,
                input_text_data,
                context,
            )
        except:
            _LOGGER.exception("Setting input_text failed")


    async def async_input_boolean_turn_on(self, context: Context, entity_id: str):
        self._debug(f"Turning on input_boolean '{entity_id}'")
        try:
            input_boolean_data = {
                ATTR_ENTITY_ID: f"input_boolean.{entity_id}",
            }
            await self.react.hass.services.async_call(
                BOOLEAN_DOMAIN,
                SERVICE_TURN_ON,
                input_boolean_data,
                context,
            )
        except:
            _LOGGER.exception("Turning on input_boolean failed")


    async def async_input_boolean_turn_off(self, context: Context, entity_id: str):
        self._debug(f"Turning off input_boolean '{entity_id}'")
        try:
            input_boolean_data = {
                ATTR_ENTITY_ID: f"input_boolean.{entity_id}",
            }
            await self.react.hass.services.async_call(
                BOOLEAN_DOMAIN,
                SERVICE_TURN_OFF,
                input_boolean_data,
                context,
            )
        except:
            _LOGGER.exception("Turning off input_boolean failed")


    async def async_input_boolean_toggle(self, context: Context, entity_id: str):
        self._debug(f"Toggling input_boolean '{entity_id}'")
        try:
            input_boolean_data = {
                ATTR_ENTITY_ID: f"input_boolean.{entity_id}",
            }
            await self.react.hass.services.async_call(
                BOOLEAN_DOMAIN,
                SERVICE_TOGGLE,
                input_boolean_data,
                context,
            )
        except:
            _LOGGER.exception("Toggling input_boolean failed")
