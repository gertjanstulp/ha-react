from homeassistant.const import (
    STATE_OFF,
    STATE_ON
)
from homeassistant.core import Context

from custom_components.react.plugin.const import PROVIDER_TYPE_LIGHT
from custom_components.react.plugin.light.config import LightConfig
from custom_components.react.plugin.light.const import LIGHT_GENERIC_PROVIDER
from custom_components.react.plugin.light.provider import LightProvider
from custom_components.react.plugin.api import ApiBase, HassApi, PluginApi
from custom_components.react.utils.logger import get_react_logger


_LOGGER = get_react_logger()


class LightApi(ApiBase):
    def __init__(self, plugin_api: PluginApi, hass_api: HassApi, config: LightConfig) -> None:
        super().__init__(plugin_api, hass_api)
        self.config = config


    def _debug(self, message: str):
        _LOGGER.debug(f"Light plugin: Api - {message}")


    async def async_light_turn_on(self, context: Context, entity_id: str, light_provider: str):
        self._debug(f"Turning on light '{entity_id}'")
        try:
            full_entity_id = f"light.{entity_id}"
            if state := self.hass_api.hass_get_state(full_entity_id):
                value = state.state
            else:
                _LOGGER.warn(f"Light plugin: Api - {full_entity_id} not found")
                return
            
            provider = self.get_light_provider(light_provider)
            if provider and value is not None and value == STATE_OFF:
                await provider.async_set_state(context, full_entity_id, STATE_ON)
        except:
            _LOGGER.exception("Turning on light failed")


    async def async_light_turn_off(self, context: Context, entity_id: str, light_provider: str):
        self._debug(f"Turning off light '{entity_id}'")
        try:
            full_entity_id = f"light.{entity_id}"
            if state := self.hass_api.hass_get_state(full_entity_id):
                value = state.state
            else:
                _LOGGER.warn(f"Light plugin: Api - {full_entity_id} not found")
                return
            
            provider = self.get_light_provider(light_provider)
            if provider and value is not None and value == STATE_ON:
                await provider.async_set_state(context, full_entity_id, STATE_OFF)
        except:
            _LOGGER.exception("Turning off light failed")


    async def async_light_toggle(self, context: Context, entity_id: str, light_provider: str):
        self._debug(f"Toggling light '{entity_id}'")
        try:
            full_entity_id = f"light.{entity_id}"
            if state := self.hass_api.hass_get_state(full_entity_id):
                value = state.state
            else:
                _LOGGER.warn(f"Light plugin: Api - {full_entity_id} not found")
                return
            
            provider = self.get_light_provider(light_provider)
            if provider and value is not None:
                await provider.async_set_state(context, full_entity_id, STATE_ON if value == STATE_OFF else STATE_OFF)
        except:
            _LOGGER.exception("Toggling light failed")


    def get_light_provider(self, light_provider: str) -> LightProvider:
        light_provider = light_provider or self.config.light_provider or LIGHT_GENERIC_PROVIDER
        result = self.plugin_api.get_provider(PROVIDER_TYPE_LIGHT, light_provider)
        if not result:
            _LOGGER.error(f"Light plugin: Api - Light provider for '{light_provider}' not found")
            return None
        return result
