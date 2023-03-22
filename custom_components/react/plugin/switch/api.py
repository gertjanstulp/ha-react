from homeassistant.components.switch import (
    DOMAIN as SWITCH_DOMAIN,
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
        _LOGGER.debug(f"Switch plugin: Api - {message}")


    async def async_switch_turn_on(self, context: Context, entity_id: str):
        self._debug(f"Turning on switch '{entity_id}'")
        try:
            switch_data = {
                ATTR_ENTITY_ID: f"switch.{entity_id}",
            }
            await self.react.hass.services.async_call(
                SWITCH_DOMAIN,
                SERVICE_TURN_ON,
                switch_data,
                context,
            )
        except:
            _LOGGER.exception("Turning on switch failed")


    async def async_switch_turn_off(self, context: Context, entity_id: str):
        self._debug(f"Turning off switch '{entity_id}'")
        try:
            switch_data = {
                ATTR_ENTITY_ID: f"switch.{entity_id}",
            }
            await self.react.hass.services.async_call(
                SWITCH_DOMAIN,
                SERVICE_TURN_OFF,
                switch_data,
                context,
            )
        except:
            _LOGGER.exception("Turning off switch failed")


    async def async_switch_toggle(self, context: Context, entity_id: str):
        self._debug(f"Toggling switch '{entity_id}'")
        try:
            switch_data = {
                ATTR_ENTITY_ID: f"switch.{entity_id}",
            }
            await self.react.hass.services.async_call(
                SWITCH_DOMAIN,
                SERVICE_TOGGLE,
                switch_data,
                context,
            )
        except:
            _LOGGER.exception("Toggling switch failed")
