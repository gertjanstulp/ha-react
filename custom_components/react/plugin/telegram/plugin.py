from custom_components.react.plugin.const import PROVIDER_TYPE_NOTIFY
from custom_components.react.plugin.plugin_factory import HassApi, PluginApi
from custom_components.react.plugin.telegram.const import NOTIFY_PROVIDER_TELEGRAM
from custom_components.react.plugin.telegram.provider import TelegramProvider
from custom_components.react.plugin.telegram.tasks.callback_transform_in_task import CallbackTransformInTask
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData


def load(plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
    loader = TelegramPluginLoader()
    loader.load(plugin_api, hass_api, config)


class TelegramPluginLoader:
    def load(self, plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
        get_react_logger().debug(f"Telegram plugin: Loading")

        plugin_api.register_plugin_provider(
            PROVIDER_TYPE_NOTIFY, 
            NOTIFY_PROVIDER_TELEGRAM, 
            TelegramProvider(plugin_api, hass_api))
        
        plugin_api.register_plugin_task(CallbackTransformInTask)
