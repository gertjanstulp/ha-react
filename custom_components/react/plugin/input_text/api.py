from homeassistant.core import Context

from custom_components.react.plugin.const import PROVIDER_TYPE_INPUT_TEXT
from custom_components.react.plugin.input_text.config import InputTextConfig
from custom_components.react.plugin.input_text.const import INPUT_TEXT_GENERIC_PROVIDER
from custom_components.react.plugin.input_text.provider import InputTextProvider
from custom_components.react.plugin.base import PluginApiBase
from custom_components.react.utils.session import Session



class InputTextApi(PluginApiBase[InputTextConfig]):

    async def async_input_text_set(self, session: Session, context: Context, entity_id: str, value: str, input_text_provider: str = None):
        try:
            full_entity_id = f"input_text.{entity_id}"
            session.debug(self.logger, f"Setting {full_entity_id} to '{str(value)}'")
            if not self.plugin.hass_api.hass_get_state(full_entity_id):
                session.warning(self.plugin.logger, f"{full_entity_id} not found")
                return
            
            provider = self.get_input_text_provider(session, input_text_provider)
            if provider:
                await provider.async_input_text_set_value(session, context, full_entity_id, value)
        except:
            session.exception(self.logger, "Setting input_text failed")


    def get_input_text_provider(self, session: Session, input_text_provider: str) -> InputTextProvider:
        input_text_provider = input_text_provider or self.plugin.config.input_text_provider or INPUT_TEXT_GENERIC_PROVIDER
        result = self.plugin.get_provider(PROVIDER_TYPE_INPUT_TEXT, input_text_provider)
        if not result:
            session.error(self.plugin.logger, f"Input_text provider for '{input_text_provider}' not found")
            return None
        return result
