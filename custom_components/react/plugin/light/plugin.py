from custom_components.react.plugin.const import PROVIDER_TYPE_LIGHT
from custom_components.react.plugin.light.api import LightApi
from custom_components.react.plugin.light.config import LightConfig
from custom_components.react.plugin.light.const import LIGHT_GENERIC_PROVIDER
from custom_components.react.plugin.light.provider import LightProvider
from custom_components.react.plugin.light.tasks.light_turn_on_task import LightTurnOnTask
from custom_components.react.plugin.light.tasks.light_turn_off_task import LightTurnOffTask
from custom_components.react.plugin.light.tasks.light_toggle_task import LightToggleTask
from custom_components.react.plugin.plugin_factory import HassApi, PluginApi
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData

_LOGGER = get_react_logger()

def load(plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
    loader = LightPluginLoader()
    loader.load(plugin_api, hass_api, config)


class LightPluginLoader:
    def load(self, plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
        _LOGGER.debug(f"Light plugin: Loading")

        api = LightApi(plugin_api, hass_api, LightConfig(config))

        plugin_api.register_plugin_provider(
            PROVIDER_TYPE_LIGHT, 
            LIGHT_GENERIC_PROVIDER,
            LightProvider(plugin_api, hass_api))
        
        plugin_api.register_plugin_task(LightTurnOnTask, api=api)
        plugin_api.register_plugin_task(LightTurnOffTask, api=api)
        plugin_api.register_plugin_task(LightToggleTask, api=api)