from homeassistant.const import (
    STATE_OFF,
    STATE_ON
)
from homeassistant.core import Context

from custom_components.react.plugin.const import PROVIDER_TYPE_SWITCH
from custom_components.react.plugin.plugin_factory import ApiBase, HassApi, PluginApi
from custom_components.react.plugin.switch.const import SWITCH_GENERIC_PROVIDER
from custom_components.react.plugin.switch.provider import SwitchProvider
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData


_LOGGER = get_react_logger()


class SwitchConfig(DynamicData):
    def __init__(self, source: DynamicData = None) -> None:
        super().__init__()
        self.switch_provider_name: str = None
        self.load(source)


class SwitchApi(ApiBase):
    def __init__(self, plugin_api: PluginApi, hass_api: HassApi, config: SwitchConfig) -> None:
        super().__init__(plugin_api, hass_api)
        self.config = config


    def _debug(self, message: str):
        _LOGGER.debug(f"Switch plugin: Api - {message}")


    async def async_switch_turn_on(self, context: Context, entity_id: str, switch_provider_name: str):
        self._debug(f"Turning on switch '{entity_id}'")
        try:
            full_entity_id = f"switch.{entity_id}"
            if state := self.hass_api.hass_get_state(full_entity_id):
                value = state.state
            else:
                _LOGGER.warn(f"Switch plugin: Api - {full_entity_id} not found")
                return
            
            switch_provider = self.get_switch_provider(switch_provider_name)
            if switch_provider and value is not None and value == STATE_OFF:
                await switch_provider.async_set_state(context, full_entity_id, STATE_ON)
        except:
            _LOGGER.exception("Turning on switch failed")


    async def async_switch_turn_off(self, context: Context, entity_id: str, switch_provider_name: str):
        self._debug(f"Turning off switch '{entity_id}'")
        try:
            full_entity_id = f"switch.{entity_id}"
            if state := self.hass_api.hass_get_state(full_entity_id):
                value = state.state
            else:
                _LOGGER.warn(f"Switch plugin: Api - {full_entity_id} not found")
                return
            
            switch_provider = self.get_switch_provider(switch_provider_name)
            if switch_provider and value is not None and value == STATE_ON:
                await switch_provider.async_set_state(context, full_entity_id, STATE_OFF)
        except:
            _LOGGER.exception("Turning off switch failed")


    async def async_switch_toggle(self, context: Context, entity_id: str, switch_provider_name: str):
        self._debug(f"Toggling switch '{entity_id}'")
        try:
            full_entity_id = f"switch.{entity_id}"
            if state := self.hass_api.hass_get_state(full_entity_id):
                value = state.state
            else:
                _LOGGER.warn(f"Switch plugin: Api - {full_entity_id} not found")
                return
            
            switch_provider = self.get_switch_provider(switch_provider_name)
            if switch_provider and value is not None:
                await switch_provider.async_set_state(context, full_entity_id, STATE_ON if value == STATE_OFF else STATE_OFF)
        except:
            _LOGGER.exception("Toggling switch failed")


    def get_switch_provider(self, switch_provider_name: str) -> SwitchProvider:
        switch_provider_name = switch_provider_name or self.config.switch_provider_name or SWITCH_GENERIC_PROVIDER
        result = self.plugin_api.get_provider(PROVIDER_TYPE_SWITCH, switch_provider_name)
        if not result:
            _LOGGER.error(f"Switch plugin: Api - Switch provider for '{switch_provider_name}' not found")
            return None
        return result

