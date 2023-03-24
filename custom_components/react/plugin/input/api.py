import numbers
from homeassistant.components.input_number import (
    DOMAIN as NUMBER_DOMAIN,
    SERVICE_SET_VALUE as NUMBER_SERVICE_SET_VALUE,
    ATTR_VALUE as NUMBER_ATTR_VALUE,
)
from homeassistant.const import (
    ATTR_ENTITY_ID, 
    STATE_OFF,
    STATE_ON
)
from homeassistant.core import Context

from custom_components.react.base import ReactBase
from custom_components.react.plugin.input.service import Service
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData


_LOGGER = get_react_logger()


class ApiConfig(DynamicData):
    def __init__(self, source: DynamicData = None) -> None:
        super().__init__()
        self.load(source)


class Api():
    def __init__(self, react: ReactBase, config: ApiConfig, service: Service) -> None:
        self.react = react
        self.config = config
        self.service = service


    def _debug(self, message: str):
        _LOGGER.debug(f"Input plugin: Api - {message}")


    async def async_input_number_set(self, context: Context, entity_id: str, value: float):
        self._debug(f"Setting input_number '{entity_id}' to '{str(value)}'")
        try:
            full_entity_id = f"input_number.{entity_id}"
            await self.service.async_input_number_set_value(context, full_entity_id, value)
        except:
            _LOGGER.exception("Setting input_number failed")


    async def async_input_number_increase(self, context: Context, entity_id: str, increase: float, max: float = None):
        self._debug(f"Increasing input_number '{entity_id}' with '{str(increase)}'")
        try:
            full_entity_id = f"input_number.{entity_id}"
            value: float = None
            if state := self.react.hass.states.get(full_entity_id):
                try:
                    value = float(state.state) + increase
                    if max and value > max:
                        value = max
                except ValueError:
                    _LOGGER.warn(f"Input plugin: Api - {full_entity_id} has no numeric value, could not increase")
            else:
                _LOGGER.warn(f"Input plugin: Api - {full_entity_id} not found")
                            
            if value:
                await self.service.async_input_number_set_value(context, full_entity_id, value)
        except:
            _LOGGER.exception("Increasing input_number failed")


    async def async_input_number_decrease(self, context: Context, entity_id: str, decrease: float, min: float = None):
        self._debug(f"Increasing input_number '{entity_id}' with '{str(decrease)}'")
        try:
            full_entity_id = f"input_number.{entity_id}"
            value: float = None
            if state := self.react.hass.states.get(full_entity_id):
                try:
                    value = float(state.state) - decrease
                    if min and value < min:
                        value = min
                except ValueError:
                    _LOGGER.warn(f"Input plugin: Api - {full_entity_id} has no numeric value, could not decrease")
            else:
                _LOGGER.warn(f"Input plugin: Api - {full_entity_id} not found")
                            
            if value:
                await self.service.async_input_number_set_value(context, full_entity_id, value)
        except:
            _LOGGER.exception("Decreasing input_number failed")


    async def async_input_text_set(self, context: Context, entity_id: str, value: str):
        self._debug(f"Setting input_text '{entity_id}' to '{str(value)}'")
        try:
            full_entity_id = f"input_text.{entity_id}"
            await self.service.async_input_text_set_value(context, full_entity_id, value)
        except:
            _LOGGER.exception("Setting input_text failed")


    async def async_input_boolean_turn_on(self, context: Context, entity_id: str):
        self._debug(f"Turning on input_boolean '{entity_id}'")
        try:
            full_entity_id = f"input_boolean.{entity_id}"
            value: bool = None
            if state := self.react.hass.states.get(full_entity_id):
                try:
                    value = state.state
                except ValueError:
                    _LOGGER.warn(f"Input plugin: Api - {full_entity_id} has no bool value, could not turn on")
            else:
                _LOGGER.warn(f"Input plugin: Api - {full_entity_id} not found")
            
            if value is not None and value == STATE_OFF:
                await self.service.async_input_boolean_set_value(context, full_entity_id, STATE_ON)
        except:
            _LOGGER.exception("Turning on input_boolean failed")


    async def async_input_boolean_turn_off(self, context: Context, entity_id: str):
        self._debug(f"Turning off input_boolean '{entity_id}'")
        try:
            full_entity_id = f"input_boolean.{entity_id}"
            value: bool = None
            if state := self.react.hass.states.get(full_entity_id):
                try:
                    value = state.state
                except ValueError:
                    _LOGGER.warn(f"Input plugin: Api - {full_entity_id} has no bool value, could not turn off")
            else:
                _LOGGER.warn(f"Input plugin: Api - {full_entity_id} not found")
            
            if value is not None and value == STATE_ON:
                await self.service.async_input_boolean_set_value(context, full_entity_id, STATE_OFF)
        except:
            _LOGGER.exception("Turning off input_boolean failed")


    async def async_input_boolean_toggle(self, context: Context, entity_id: str):
        self._debug(f"Toggling input_boolean '{entity_id}'")
        try:
            full_entity_id = f"input_boolean.{entity_id}"
            value: bool = None
            if state := self.react.hass.states.get(full_entity_id):
                try:
                    value = state.state
                except ValueError:
                    _LOGGER.warn(f"Input plugin: Api - {full_entity_id} has no bool value, could not turn on")
            else:
                _LOGGER.warn(f"Input plugin: Api - {full_entity_id} not found")
            
            if value is not None:
                await self.service.async_input_boolean_set_value(context, full_entity_id, STATE_ON if value == STATE_OFF else STATE_OFF)
        except:
            _LOGGER.exception("Toggling input_boolean failed")
