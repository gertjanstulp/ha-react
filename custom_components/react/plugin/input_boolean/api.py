from homeassistant.const import (
    STATE_OFF,
    STATE_ON
)
from homeassistant.core import Context

from custom_components.react.plugin.const import PROVIDER_TYPE_INPUT_BOOLEAN
from custom_components.react.plugin.input_boolean.config import InputBooleanConfig
from custom_components.react.plugin.input_boolean.const import INPUT_BOOLEAN_GENERIC_PROVIDER
from custom_components.react.plugin.input_boolean.provider import InputBooleanProvider
from custom_components.react.plugin.base import PluginApiBase
from custom_components.react.utils.logger import get_react_logger


_LOGGER = get_react_logger()


class InputBooleanApi(PluginApiBase[InputBooleanConfig]):

    def _debug(self, message: str):
        _LOGGER.debug(f"Input boolean plugin: Api - {message}")


    async def async_input_boolean_turn_on(self, context: Context, entity_id: str, input_boolean_provider: str = None):
        self._debug(f"Turning on input_boolean '{entity_id}'")
        try:
            full_entity_id = f"input_boolean.{entity_id}"
            value: bool = None
            if state := self.plugin.hass_api.hass_get_state(full_entity_id):
                try:
                    value = state.state
                except ValueError:
                    _LOGGER.warn(f"Input boolean plugin: Api - {full_entity_id} has no bool value, could not turn on")
            else:
                _LOGGER.warn(f"Input boolean plugin: Api - {full_entity_id} not found")
            
            provider = self.get_input_boolean_provider(input_boolean_provider)
            if provider and value is not None and value == STATE_OFF:
                await provider.async_input_boolean_set_value(context, full_entity_id, STATE_ON)
        except:
            _LOGGER.exception("Turning on input_boolean failed")


    async def async_input_boolean_turn_off(self, context: Context, entity_id: str, input_boolean_provider: str = None):
        self._debug(f"Turning off input_boolean '{entity_id}'")
        try:
            full_entity_id = f"input_boolean.{entity_id}"
            value: bool = None
            if state := self.plugin.hass_api.hass_get_state(full_entity_id):
                try:
                    value = state.state
                except ValueError:
                    _LOGGER.warn(f"Input boolean plugin: Api - {full_entity_id} has no bool value, could not turn off")
            else:
                _LOGGER.warn(f"Input boolean plugin: Api - {full_entity_id} not found")
            
            provider = self.get_input_boolean_provider(input_boolean_provider)
            if provider and value is not None and value == STATE_ON:
                await provider.async_input_boolean_set_value(context, full_entity_id, STATE_OFF)
        except:
            _LOGGER.exception("Turning off input_boolean failed")


    async def async_input_boolean_toggle(self, context: Context, entity_id: str, input_boolean_provider: str = None):
        self._debug(f"Toggling input_boolean '{entity_id}'")
        try:
            full_entity_id = f"input_boolean.{entity_id}"
            value: bool = None
            if state := self.plugin.hass_api.hass_get_state(full_entity_id):
                try:
                    value = state.state
                except ValueError:
                    _LOGGER.warn(f"Input boolean plugin: Api - {full_entity_id} has no bool value, could not turn on")
            else:
                _LOGGER.warn(f"Input boolean plugin: Api - {full_entity_id} not found")
            
            provider = self.get_input_boolean_provider(input_boolean_provider)
            if provider and value is not None:
                await provider.async_input_boolean_set_value(context, full_entity_id, STATE_ON if value == STATE_OFF else STATE_OFF)
        except:
            _LOGGER.exception("Toggling input_boolean failed")


    def get_input_boolean_provider(self, input_boolean_provider: str) -> InputBooleanProvider:
        input_boolean_provider = input_boolean_provider or self.plugin.config.input_boolean_provider or INPUT_BOOLEAN_GENERIC_PROVIDER
        result = self.plugin.get_provider(PROVIDER_TYPE_INPUT_BOOLEAN, input_boolean_provider)
        if not result:
            _LOGGER.error(f"Input boolean plugin: Api - Input boolean provider for '{input_boolean_provider}' not found")
            return None
        return result
