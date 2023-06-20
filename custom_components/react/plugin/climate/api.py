from homeassistant.const import ATTR_TEMPERATURE
from homeassistant.core import Context
from custom_components.react.plugin.climate.const import CLIMATE_GENERIC_PROVIDER

from custom_components.react.plugin.const import PROVIDER_TYPE_CLIMATE
from custom_components.react.plugin.climate.config import ClimateConfig
from custom_components.react.plugin.climate.provider import ClimateProvider
from custom_components.react.plugin.base import PluginApiBase
from custom_components.react.utils.session import Session
from custom_components.react.utils.struct import DynamicData


class ClimateApi(PluginApiBase[ClimateConfig]):

    async def async_set_temperature(self,
        session: Session,
        context: Context, 
        entity_id: str, 
        temperature: float,
        climate_provider: str,
    ):
        try:
            full_entity_id = f"climate.{entity_id}"
            session.debug(self.logger, f"Setting temperature of {full_entity_id} to {temperature}")
            if state := self.plugin.hass_api.hass_get_state(full_entity_id):
                state_temperature = state.attributes.get(ATTR_TEMPERATURE, None)
            else:
                session.warning(self.plugin.logger, f"{full_entity_id} not found")
                return
            
            if provider := self.get_climate_provider(session, full_entity_id, climate_provider):
                if temperature != state_temperature:
                    await provider.async_set_temperature(session, context, full_entity_id, temperature)
        except:
            session.exception(self.logger, "Setting temperature failed")
    

    async def async_reset_temperature(self,
        session: Session,
        context: Context, 
        entity_id: str, 
        climate_provider: str,
    ):
        try:
            full_entity_id = f"climate.{entity_id}"
            session.debug(self.logger, f"Resetting temperature of {full_entity_id}")
            if state := self.plugin.hass_api.hass_get_state(full_entity_id):
                state_temperature = state.attributes.get(ATTR_TEMPERATURE, None)
            else:
                session.warning(self.plugin.logger, f"{full_entity_id} not found")
                return
            
            if provider := self.get_climate_provider(session, full_entity_id, climate_provider, False):
                await provider.async_reset_temperature(session, context, full_entity_id)
        except:
            session.exception(self.logger, "Resetting temperature failed")


    def get_climate_provider(self, session: Session, full_entity_id: str, climate_provider: str, include_generic: bool = True) -> ClimateProvider:
        result = None
    
        entity = self.plugin.hass_api.hass_get_entity(full_entity_id)
        if entity:
            result = self.plugin.get_provider(PROVIDER_TYPE_CLIMATE, entity.platform)
        
        if not result:
            climate_provider = climate_provider or self.plugin.config.climate_provider 
            if not climate_provider and include_generic:
                climate_provider = CLIMATE_GENERIC_PROVIDER
            if climate_provider:
                result = self.plugin.get_provider(PROVIDER_TYPE_CLIMATE, climate_provider)
    
        if not result:
            target = full_entity_id
            if climate_provider:
                target = f"{target}/{climate_provider}"
            session.error(self.plugin.logger, f"Climate provider for {target} not found")
            return None
        return result
