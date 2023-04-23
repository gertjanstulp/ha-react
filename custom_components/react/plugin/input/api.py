from homeassistant.const import (
    STATE_OFF,
    STATE_ON
)
from homeassistant.core import Context

from custom_components.react.plugin.const import PROVIDER_TYPE_INPUT
from custom_components.react.plugin.input.config import InputConfig
from custom_components.react.plugin.input.const import INPUT_GENERIC_PROVIDER
from custom_components.react.plugin.input.provider import InputProvider
from custom_components.react.plugin.plugin_factory import ApiBase, HassApi, PluginApi
from custom_components.react.utils.logger import get_react_logger


_LOGGER = get_react_logger()


class InputApi(ApiBase):
    def __init__(self, plugin_api: PluginApi, hass_api: HassApi, config: InputConfig) -> None:
        super().__init__(plugin_api, hass_api)
        self.config = config


    def _debug(self, message: str):
        _LOGGER.debug(f"Input plugin: Api - {message}")


    async def async_input_number_set(self, context: Context, entity_id: str, value: float, input_provider_name: str = None):
        self._debug(f"Setting input_number '{entity_id}' to '{str(value)}'")
        try:
            full_entity_id = f"input_number.{entity_id}"
            if not self.hass_api.hass_get_state(full_entity_id):
                _LOGGER.warn(f"Input plugin: Api - {full_entity_id} not found")
                return
            
            input_provider = self.get_input_provider(input_provider_name)
            if input_provider:
                await input_provider.async_input_number_set_value(context, full_entity_id, value)
        except:
            _LOGGER.exception("Setting input_number failed")


    async def async_input_number_increase(self, context: Context, entity_id: str, increase: float, max: float = None, input_provider_name: str = None):
        self._debug(f"Increasing input_number '{entity_id}' with '{str(increase)}'")
        try:
            full_entity_id = f"input_number.{entity_id}"
            value: float = None
            if state := self.hass_api.hass_get_state(full_entity_id):
                try:
                    value = float(state.state) + increase
                    if max and value > max:
                        value = max
                except ValueError:
                    _LOGGER.warn(f"Input plugin: Api - {full_entity_id} has no numeric value, could not increase")
            else:
                _LOGGER.warn(f"Input plugin: Api - {full_entity_id} not found")
                            
            input_provider = self.get_input_provider(input_provider_name)
            if input_provider and value:
                await input_provider.async_input_number_set_value(context, full_entity_id, value)
        except:
            _LOGGER.exception("Increasing input_number failed")


    async def async_input_number_decrease(self, context: Context, entity_id: str, decrease: float, min: float = None, input_provider_name: str = None):
        self._debug(f"Increasing input_number '{entity_id}' with '{str(decrease)}'")
        try:
            full_entity_id = f"input_number.{entity_id}"
            value: float = None
            if state := self.hass_api.hass_get_state(full_entity_id):
                try:
                    value = float(state.state) - decrease
                    if min and value < min:
                        value = min
                except ValueError:
                    _LOGGER.warn(f"Input plugin: Api - {full_entity_id} has no numeric value, could not decrease")
            else:
                _LOGGER.warn(f"Input plugin: Api - {full_entity_id} not found")
                            
            input_provider = self.get_input_provider(input_provider_name)
            if input_provider and value:
                await input_provider.async_input_number_set_value(context, full_entity_id, value)
        except:
            _LOGGER.exception("Decreasing input_number failed")


    async def async_input_text_set(self, context: Context, entity_id: str, value: str, input_provider_name: str = None):
        self._debug(f"Setting input_text '{entity_id}' to '{str(value)}'")
        try:
            full_entity_id = f"input_text.{entity_id}"
            if not self.hass_api.hass_get_state(full_entity_id):
                _LOGGER.warn(f"Input plugin: Api - {full_entity_id} not found")
                return
            
            input_provider = self.get_input_provider(input_provider_name)
            if input_provider:
                await input_provider.async_input_text_set_value(context, full_entity_id, value)
        except:
            _LOGGER.exception("Setting input_text failed")


    async def async_input_boolean_turn_on(self, context: Context, entity_id: str, input_provider_name: str = None):
        self._debug(f"Turning on input_boolean '{entity_id}'")
        try:
            full_entity_id = f"input_boolean.{entity_id}"
            value: bool = None
            if state := self.hass_api.hass_get_state(full_entity_id):
                try:
                    value = state.state
                except ValueError:
                    _LOGGER.warn(f"Input plugin: Api - {full_entity_id} has no bool value, could not turn on")
            else:
                _LOGGER.warn(f"Input plugin: Api - {full_entity_id} not found")
            
            input_provider = self.get_input_provider(input_provider_name)
            if input_provider and value is not None and value == STATE_OFF:
                await input_provider.async_input_boolean_set_value(context, full_entity_id, STATE_ON)
        except:
            _LOGGER.exception("Turning on input_boolean failed")


    async def async_input_boolean_turn_off(self, context: Context, entity_id: str, input_provider_name: str = None):
        self._debug(f"Turning off input_boolean '{entity_id}'")
        try:
            full_entity_id = f"input_boolean.{entity_id}"
            value: bool = None
            if state := self.hass_api.hass_get_state(full_entity_id):
                try:
                    value = state.state
                except ValueError:
                    _LOGGER.warn(f"Input plugin: Api - {full_entity_id} has no bool value, could not turn off")
            else:
                _LOGGER.warn(f"Input plugin: Api - {full_entity_id} not found")
            
            input_provider = self.get_input_provider(input_provider_name)
            if input_provider and value is not None and value == STATE_ON:
                await input_provider.async_input_boolean_set_value(context, full_entity_id, STATE_OFF)
        except:
            _LOGGER.exception("Turning off input_boolean failed")


    async def async_input_boolean_toggle(self, context: Context, entity_id: str, input_provider_name: str = None):
        self._debug(f"Toggling input_boolean '{entity_id}'")
        try:
            full_entity_id = f"input_boolean.{entity_id}"
            value: bool = None
            if state := self.hass_api.hass_get_state(full_entity_id):
                try:
                    value = state.state
                except ValueError:
                    _LOGGER.warn(f"Input plugin: Api - {full_entity_id} has no bool value, could not turn on")
            else:
                _LOGGER.warn(f"Input plugin: Api - {full_entity_id} not found")
            
            input_provider = self.get_input_provider(input_provider_name)
            if input_provider and value is not None:
                await input_provider.async_input_boolean_set_value(context, full_entity_id, STATE_ON if value == STATE_OFF else STATE_OFF)
        except:
            _LOGGER.exception("Toggling input_boolean failed")


    def get_input_provider(self, input_provider_name: str) -> InputProvider:
        input_provider_name = input_provider_name or self.config.input_provider_name or INPUT_GENERIC_PROVIDER
        result = self.plugin_api.get_provider(PROVIDER_TYPE_INPUT, input_provider_name)
        if not result:
            _LOGGER.error(f"Input plugin: Api - Input provider for '{input_provider_name}' not found")
            return None
        return result
