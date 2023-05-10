from homeassistant.core import Context

from custom_components.react.plugin.const import PROVIDER_TYPE_INPUT_NUMBER
from custom_components.react.plugin.input_number.config import InputNumberConfig
from custom_components.react.plugin.input_number.const import INPUT_NUMBER_GENERIC_PROVIDER
from custom_components.react.plugin.input_number.provider import InputNumberProvider
from custom_components.react.plugin.base import PluginApiBase
from custom_components.react.utils.logger import get_react_logger


_LOGGER = get_react_logger()


class InputNumberApi(PluginApiBase[InputNumberConfig]):

    def _debug(self, message: str):
        _LOGGER.debug(f"Input number plugin: Api - {message}")


    async def async_input_number_set(self, context: Context, entity_id: str, value: float, input_number_provider: str = None):
        self._debug(f"Setting input_number '{entity_id}' to '{str(value)}'")
        try:
            full_entity_id = f"input_number.{entity_id}"
            if not self.plugin.hass_api.hass_get_state(full_entity_id):
                _LOGGER.warn(f"Input number plugin: Api - {full_entity_id} not found")
                return
            
            provider = self.get_input_number_provider(input_number_provider)
            if provider:
                await provider.async_input_number_set_value(context, full_entity_id, value)
        except:
            _LOGGER.exception("Setting input_number failed")


    async def async_input_number_increase(self, context: Context, entity_id: str, increase: float, max: float = None, input_number_provider: str = None):
        self._debug(f"Increasing input_number '{entity_id}' with '{str(increase)}'")
        try:
            full_entity_id = f"input_number.{entity_id}"
            value: float = None
            if state := self.plugin.hass_api.hass_get_state(full_entity_id):
                try:
                    value = float(state.state) + increase
                    if max and value > max:
                        value = max
                except ValueError:
                    _LOGGER.warn(f"Input number plugin: Api - {full_entity_id} has no numeric value, could not increase")
            else:
                _LOGGER.warn(f"Input number plugin: Api - {full_entity_id} not found")
                            
            provider = self.get_input_number_provider(input_number_provider)
            if provider and value:
                await provider.async_input_number_set_value(context, full_entity_id, value)
        except:
            _LOGGER.exception("Increasing input_number failed")


    async def async_input_number_decrease(self, context: Context, entity_id: str, decrease: float, min: float = None, input_number_provider: str = None):
        self._debug(f"Increasing input_number '{entity_id}' with '{str(decrease)}'")
        try:
            full_entity_id = f"input_number.{entity_id}"
            value: float = None
            if state := self.plugin.hass_api.hass_get_state(full_entity_id):
                try:
                    value = float(state.state) - decrease
                    if min and value < min:
                        value = min
                except ValueError:
                    _LOGGER.warn(f"Input number plugin: Api - {full_entity_id} has no numeric value, could not decrease")
            else:
                _LOGGER.warn(f"Input number plugin: Api - {full_entity_id} not found")
                            
            provider = self.get_input_number_provider(input_number_provider)
            if provider and value:
                await provider.async_input_number_set_value(context, full_entity_id, value)
        except:
            _LOGGER.exception("Decreasing input_number failed")


    def get_input_number_provider(self, input_number_provider: str) -> InputNumberProvider:
        input_number_provider = input_number_provider or self.plugin.config.input_number_provider or INPUT_NUMBER_GENERIC_PROVIDER
        result = self.plugin.get_provider(PROVIDER_TYPE_INPUT_NUMBER, input_number_provider)
        if not result:
            _LOGGER.error(f"Input number plugin: Api - Input number provider for '{input_number_provider}' not found")
            return None
        return result
