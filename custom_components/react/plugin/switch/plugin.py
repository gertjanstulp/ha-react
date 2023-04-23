from custom_components.react.plugin.const import PROVIDER_TYPE_SWITCH
from custom_components.react.plugin.switch.const import SWITCH_GENERIC_PROVIDER
from custom_components.react.plugin.switch.provider import SwitchProvider
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData

from custom_components.react.plugin.plugin_factory import HassApi, PluginApi
from custom_components.react.plugin.switch.api import SwitchApi, SwitchConfig
from custom_components.react.plugin.switch.tasks.switch_turn_on_task import SwitchTurnOnTask
from custom_components.react.plugin.switch.tasks.switch_turn_off_task import SwitchTurnOffTask
from custom_components.react.plugin.switch.tasks.switch_toggle_task import SwitchToggleTask

_LOGGER = get_react_logger()

def load(plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
    loader = SwitchPluginLoader()
    loader.load(plugin_api, hass_api, config)


class SwitchPluginLoader:
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