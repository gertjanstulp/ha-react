from homeassistant.components.input_number import (
    DOMAIN,
    SERVICE_SET_VALUE,
    ATTR_VALUE
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
                ATTR_VALUE: value,
            }
            await self.react.hass.services.async_call(
                DOMAIN,
                SERVICE_SET_VALUE,
                input_number_data,
                context,
            )
        except:
            _LOGGER.exception("Setting input_number failed")
