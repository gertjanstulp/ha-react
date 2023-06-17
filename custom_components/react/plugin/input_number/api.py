from homeassistant.core import Context

from custom_components.react.plugin.const import PROVIDER_TYPE_INPUT_NUMBER
from custom_components.react.plugin.input_number.config import InputNumberConfig
from custom_components.react.plugin.input_number.const import INPUT_NUMBER_GENERIC_PROVIDER
from custom_components.react.plugin.input_number.provider import InputNumberProvider
from custom_components.react.plugin.base import PluginApiBase
from custom_components.react.utils.session import Session



class InputNumberApi(PluginApiBase[InputNumberConfig]):

    async def async_input_number_set(self, session: Session, context: Context, entity_id: str, value: float, input_number_provider: str = None):
        try:
            full_entity_id = f"input_number.{entity_id}"
            session.debug(self.logger, f"Setting {full_entity_id} to {str(value)}")
            if not self.plugin.hass_api.hass_get_state(full_entity_id):
                session.warning(self.plugin.logger, f"{full_entity_id} not found")
                return
            
            provider = self.get_input_number_provider(session, input_number_provider)
            if provider:
                await provider.async_input_number_set_value(session, context, full_entity_id, value)
        except:
            session.exception("Setting input_number failed")


    async def async_input_number_increase(self, session: Session, context: Context, entity_id: str, increase: float, max: float = None, input_number_provider: str = None):
        try:
            full_entity_id = f"input_number.{entity_id}"
            session.debug(self.logger, f"Increasing {full_entity_id} with {str(increase)}")
            value: float = None
            if state := self.plugin.hass_api.hass_get_state(full_entity_id):
                try:
                    value = float(state.state) + increase
                    if max and value > max:
                        value = max
                except ValueError:
                    session.warning(self.plugin.logger, f"{full_entity_id} has no numeric value, could not increase")
            else:
                session.warning(self.plugin.logger, f"{full_entity_id} not found")
                            
            provider = self.get_input_number_provider(session, input_number_provider)
            if provider and value:
                await provider.async_input_number_set_value(session, context, full_entity_id, value)
        except:
            session.exception("Increasing input_number failed")


    async def async_input_number_decrease(self, session: Session, context: Context, entity_id: str, decrease: float, min: float = None, input_number_provider: str = None):
        try:
            full_entity_id = f"input_number.{entity_id}"
            session.debug(self.logger, f"Decreasing {full_entity_id} with {str(decrease)}")
            value: float = None
            if state := self.plugin.hass_api.hass_get_state(full_entity_id):
                try:
                    value = float(state.state) - decrease
                    if min and value < min:
                        value = min
                except ValueError:
                    session.warning(self.plugin.logger, f"{full_entity_id} has no numeric value, could not decrease")
            else:
                session.warning(self.plugin.logger, f"{full_entity_id} not found")
                            
            provider = self.get_input_number_provider(session, input_number_provider)
            if provider and value:
                await provider.async_input_number_set_value(session, context, full_entity_id, value)
        except:
            session.exception("Decreasing input_number failed")


    def get_input_number_provider(self, session: Session, input_number_provider: str) -> InputNumberProvider:
        input_number_provider = input_number_provider or self.plugin.config.input_number_provider or INPUT_NUMBER_GENERIC_PROVIDER
        result = self.plugin.get_provider(PROVIDER_TYPE_INPUT_NUMBER, input_number_provider)
        if not result:
            session.error(self.plugin.logger, f"Input_number provider for '{input_number_provider}' not found")
            return None
        return result
