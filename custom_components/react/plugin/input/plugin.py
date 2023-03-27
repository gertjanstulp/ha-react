from custom_components.react.plugin.input.service import InputService
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData
from custom_components.react.plugin.plugin_factory import PluginApi

from custom_components.react.plugin.input.api import InputApi, InputApiConfig
from custom_components.react.plugin.input.tasks.input_number_decrease_task import InputNumberDecreaseTask
from custom_components.react.plugin.input.tasks.input_number_increase_task import InputNumberIncreaseTask
from custom_components.react.plugin.input.tasks.input_number_set_task import InputNumberSetTask
from custom_components.react.plugin.input.tasks.input_text_set_task import InputTextSetTask
from custom_components.react.plugin.input.tasks.input_boolean_turn_on_task import InputBooleanTurnOnTask
from custom_components.react.plugin.input.tasks.input_boolean_turn_off_task import InputBooleanTurnOffTask
from custom_components.react.plugin.input.tasks.input_boolean_toggle_task import InputBooleanToggleTask

_LOGGER = get_react_logger()

def load(plugin_api: PluginApi, config: DynamicData):
    _LOGGER.debug(f"Input plugin: Loading")

    api = InputApi(plugin_api.react, InputApiConfig(config), InputService(plugin_api.react))
    
    plugin_api.register_plugin_task(InputNumberSetTask, api=api)
    plugin_api.register_plugin_task(InputNumberIncreaseTask, api=api)
    plugin_api.register_plugin_task(InputNumberDecreaseTask, api=api)
    plugin_api.register_plugin_task(InputTextSetTask, api=api)
    plugin_api.register_plugin_task(InputBooleanTurnOnTask, api=api)
    plugin_api.register_plugin_task(InputBooleanTurnOffTask, api=api)
    plugin_api.register_plugin_task(InputBooleanToggleTask, api=api)