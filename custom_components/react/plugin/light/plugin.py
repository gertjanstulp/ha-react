from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData

from custom_components.react.plugin.plugin_factory import PluginApi
from custom_components.react.plugin.light.api import Api, ApiConfig
from custom_components.react.plugin.light.tasks.light_turn_on_task import LightTurnOnTask
from custom_components.react.plugin.light.tasks.light_turn_off_task import LightTurnOffTask
from custom_components.react.plugin.light.tasks.light_toggle_task import LightToggleTask

_LOGGER = get_react_logger()

def load(plugin_api: PluginApi, config: DynamicData):
    _LOGGER.debug(f"Light plugin: Loading")

    api = Api(plugin_api.react, ApiConfig(config))
    plugin_api.register_plugin_task(LightTurnOnTask, api=api)
    plugin_api.register_plugin_task(LightTurnOffTask, api=api)
    plugin_api.register_plugin_task(LightToggleTask, api=api)