import voluptuous as vol

from custom_components.react.const import CONF_ENTITY_MAPS
from custom_components.react.plugin.const import PROVIDER_TYPE_NOTIFY
from custom_components.react.plugin.api import HassApi, PluginApi
from custom_components.react.plugin.factory import PluginBase
from custom_components.react.plugin.telegram.config import TelegramConfig
from custom_components.react.plugin.telegram.const import NOTIFY_PROVIDER_TELEGRAM
from custom_components.react.plugin.telegram.provider import TelegramProvider
from custom_components.react.plugin.telegram.tasks.callback_transform_in_task import CallbackTransformInTask
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData

TELEGRAM_PLUGIN_SCHEMA = vol.Schema({
    CONF_ENTITY_MAPS: dict
})


class Plugin(PluginBase):
    def __init__(self) -> None:
        super().__init__(TELEGRAM_PLUGIN_SCHEMA)


    def load(self, plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
        get_react_logger().debug(f"Telegram plugin: Loading")

        plugin_api.register_plugin_provider(
            PROVIDER_TYPE_NOTIFY, 
            NOTIFY_PROVIDER_TELEGRAM, 
            TelegramProvider(plugin_api, hass_api))
        
        plugin_api.register_plugin_task(CallbackTransformInTask, config=TelegramConfig(config))
