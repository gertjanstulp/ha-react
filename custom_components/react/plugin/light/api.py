from homeassistant.components.light import (
    DOMAIN as LIGHT_DOMAIN,
    SERVICE_TURN_ON,
    SERVICE_TURN_OFF,
    SERVICE_TOGGLE,
)
from homeassistant.const import (
    ATTR_ENTITY_ID, 
    STATE_OFF,
    STATE_ON
)
from homeassistant.core import Context

from custom_components.react.base import ReactBase
from custom_components.react.plugin.light.service import LightService
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData


_LOGGER = get_react_logger()


class LightApiConfig(DynamicData):
    def __init__(self, source: DynamicData = None) -> None:
        super().__init__()
        self.load(source)


class LightApi():
    def __init__(self, react: ReactBase, config: LightApiConfig, service: LightService) -> None:
        self.react = react
        self.config = config
        self.service = service


    def _debug(self, message: str):
        _LOGGER.debug(f"Light plugin: Api - {message}")


    async def async_light_turn_on(self, context: Context, entity_id: str):
        self._debug(f"Turning on light '{entity_id}'")
        try:
            full_entity_id = f"light.{entity_id}"
            if state := self.react.hass.states.get(full_entity_id):
                value = state.state
            else:
                _LOGGER.warn(f"Light plugin: Api - {full_entity_id} not found")
            
            if value is not None and value == STATE_OFF:
                await self.service.async_set_state(context, full_entity_id, STATE_ON)
        except:
            _LOGGER.exception("Turning on light failed")


    async def async_light_turn_off(self, context: Context, entity_id: str):
        self._debug(f"Turning off light '{entity_id}'")
        try:
            full_entity_id = f"light.{entity_id}"
            if state := self.react.hass.states.get(full_entity_id):
                value = state.state
            else:
                _LOGGER.warn(f"Light plugin: Api - {full_entity_id} not found")
            
            if value is not None and value == STATE_ON:
                await self.service.async_set_state(context, full_entity_id, STATE_OFF)
        except:
            _LOGGER.exception("Turning off light failed")


    async def async_light_toggle(self, context: Context, entity_id: str):
        self._debug(f"Toggling light '{entity_id}'")
        try:
            full_entity_id = f"light.{entity_id}"
            if state := self.react.hass.states.get(full_entity_id):
                value = state.state
            else:
                _LOGGER.warn(f"Light plugin: Api - {full_entity_id} not found")
            
            if value is not None:
                await self.service.async_set_state(context, full_entity_id, STATE_ON if value == STATE_OFF else STATE_OFF)
        except:
            _LOGGER.exception("Toggling light failed")
