from custom_components.react.plugin.switch.service import SwitchService
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData

from custom_components.react.plugin.plugin_factory import PluginApi
from custom_components.react.plugin.switch.api import SwitchApi, SwitchApiConfig
from custom_components.react.plugin.switch.tasks.switch_turn_on_task import SwitchTurnOnTask
from custom_components.react.plugin.switch.tasks.switch_turn_off_task import SwitchTurnOffTask
from custom_components.react.plugin.switch.tasks.switch_toggle_task import SwitchToggleTask

_LOGGER = get_react_logger()

def load(plugin_api: PluginApi, config: DynamicData):
    _LOGGER.debug(f"Switch plugin: Loading")

    api = SwitchApi(plugin_api.react, SwitchApiConfig(config), SwitchService(plugin_api.react))
    plugin_api.register_plugin_task(SwitchTurnOnTask, api=api)
    plugin_api.register_plugin_task(SwitchTurnOffTask, api=api)
    plugin_api.register_plugin_task(SwitchToggleTask, api=api)