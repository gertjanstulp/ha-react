import voluptuous as vol

from homeassistant.helpers import config_validation as cv

from custom_components.react.plugin.const import PROVIDER_TYPE_SWITCH
from custom_components.react.plugin.factory import PluginBase
from custom_components.react.plugin.switch.config import SwitchConfig
from custom_components.react.plugin.switch.const import ATTR_SWITCH_PROVIDER, SWITCH_GENERIC_PROVIDER
from custom_components.react.plugin.switch.provider import SwitchProvider
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData

from custom_components.react.plugin.api import HassApi, PluginApi
from custom_components.react.plugin.switch.api import SwitchApi
from custom_components.react.plugin.switch.tasks.switch_turn_on_task import SwitchTurnOnTask
from custom_components.react.plugin.switch.tasks.switch_turn_off_task import SwitchTurnOffTask
from custom_components.react.plugin.switch.tasks.switch_toggle_task import SwitchToggleTask

_LOGGER = get_react_logger()

SWITCH_PLUGIN_CONFIG_SCHEMA = vol.Schema({
    vol.Optional(ATTR_SWITCH_PROVIDER) : cv.string,
})


class Plugin(PluginBase):
    def __init__(self) -> None:
        super().__init__(SWITCH_PLUGIN_CONFIG_SCHEMA)
        

    def load(self, plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
        _LOGGER.debug(f"Switch plugin: Loading")

        api = SwitchApi(plugin_api, hass_api, SwitchConfig(config))

        plugin_api.register_plugin_provider(
            PROVIDER_TYPE_SWITCH, 
            SWITCH_GENERIC_PROVIDER,
            SwitchProvider(plugin_api, hass_api))

        plugin_api.register_plugin_task(SwitchTurnOnTask, api=api)
        plugin_api.register_plugin_task(SwitchTurnOffTask, api=api)
        plugin_api.register_plugin_task(SwitchToggleTask, api=api)