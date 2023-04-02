from custom_components.react.plugin.const import PROVIDER_TYPE_INPUT
from custom_components.react.plugin.input.api import InputApi
from custom_components.react.plugin.input.config import InputConfig
from custom_components.react.plugin.input.const import INPUT_GENERIC_PROVIDER
from custom_components.react.plugin.input.provider import InputProvider
from custom_components.react.plugin.input.tasks.input_number_decrease_task import InputNumberDecreaseTask
from custom_components.react.plugin.input.tasks.input_number_increase_task import InputNumberIncreaseTask
from custom_components.react.plugin.input.tasks.input_number_set_task import InputNumberSetTask
from custom_components.react.plugin.input.tasks.input_text_set_task import InputTextSetTask
from custom_components.react.plugin.input.tasks.input_boolean_turn_on_task import InputBooleanTurnOnTask
from custom_components.react.plugin.input.tasks.input_boolean_turn_off_task import InputBooleanTurnOffTask
from custom_components.react.plugin.input.tasks.input_boolean_toggle_task import InputBooleanToggleTask
from custom_components.react.plugin.plugin_factory import HassApi, PluginApi
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData

_LOGGER = get_react_logger()


def load(plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
    loader = InputPluginLoader()
    loader.load(plugin_api, hass_api, config)


class InputPluginLoader:
    def load(self, plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
        _LOGGER.debug(f"Input plugin: Loading")

        api = InputApi(plugin_api, hass_api, InputConfig(config))

        plugin_api.register_plugin_provider(
            PROVIDER_TYPE_INPUT, 
            INPUT_GENERIC_PROVIDER,
            InputProvider(plugin_api, hass_api))
        
        plugin_api.register_plugin_task(InputNumberSetTask, api=api)
        plugin_api.register_plugin_task(InputNumberIncreaseTask, api=api)
        plugin_api.register_plugin_task(InputNumberDecreaseTask, api=api)
        plugin_api.register_plugin_task(InputTextSetTask, api=api)
        plugin_api.register_plugin_task(InputBooleanTurnOnTask, api=api)
        plugin_api.register_plugin_task(InputBooleanTurnOffTask, api=api)
        plugin_api.register_plugin_task(InputBooleanToggleTask, api=api)