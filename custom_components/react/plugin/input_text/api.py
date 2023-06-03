from homeassistant.core import Context

from custom_components.react.plugin.const import PROVIDER_TYPE_INPUT_TEXT
from custom_components.react.plugin.input_text.config import InputTextConfig
from custom_components.react.plugin.input_text.const import INPUT_TEXT_GENERIC_PROVIDER
from custom_components.react.plugin.input_text.provider import InputTextProvider
from custom_components.react.plugin.base import PluginApiBase
from custom_components.react.utils.logger import get_react_logger


_LOGGER = get_react_logger()


class InputTextApi(PluginApiBase[InputTextConfig]):

    def _debug(self, message: str):
        _LOGGER.debug(f"Input text plugin: Api - {message}")


    async def async_input_text_set(self, context: Context, entity_id: str, value: str, input_text_provider: str = None):
        self._debug(f"Setting input_text '{entity_id}' to '{str(value)}'")
        try:
            full_entity_id = f"input_text.{entity_id}"
            if not self.plugin.hass_api.hass_get_state(full_entity_id):
                _LOGGER.warn(f"Input text plugin: Api - {full_entity_id} not found")
                return
            
            provider = self.get_input_text_provider(input_text_provider)
            if provider:
                await provider.async_input_text_set_value(context, full_entity_id, value)
        except:
            _LOGGER.exception("Setting input_text failed")


    def get_input_text_provider(self, input_text_provider: str) -> InputTextProvider:
        input_text_provider = input_text_provider or self.plugin.config.input_text_provider or INPUT_TEXT_GENERIC_PROVIDER
        result = self.plugin.get_provider(PROVIDER_TYPE_INPUT_TEXT, input_text_provider)
        if not result:
            _LOGGER.error(f"Input text plugin: Api - Input text provider for '{input_text_provider}' not found")
            return None
        return result
