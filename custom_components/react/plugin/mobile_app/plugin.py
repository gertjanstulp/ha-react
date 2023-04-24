import voluptuous as vol

from custom_components.react.const import CONF_ENTITY_MAPS

from custom_components.react.plugin.const import PROVIDER_TYPE_NOTIFY
from custom_components.react.plugin.factory import PluginBase
from custom_components.react.plugin.mobile_app.config import MobileAppConfig
from custom_components.react.plugin.mobile_app.const import NOTIFY_PROVIDER_MOBILE_APP
from custom_components.react.plugin.mobile_app.provider import MobileAppProvider
from custom_components.react.plugin.mobile_app.tasks.callback_transform_in_task import CallbackTransformInTask
from custom_components.react.plugin.api import HassApi, PluginApi
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData

TELEGRAM_PLUGIN_SCHEMA = vol.Schema({
    CONF_ENTITY_MAPS: dict
})


class Plugin(PluginBase):
    def __init__(self) -> None:
        super().__init__(TELEGRAM_PLUGIN_SCHEMA)


    def load(self, plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
        get_react_logger().debug(f"Mobile_app plugin: Loading")
        
        plugin_api.register_plugin_provider(
            PROVIDER_TYPE_NOTIFY, 
            NOTIFY_PROVIDER_MOBILE_APP, 
            MobileAppProvider(plugin_api, hass_api))
        
        plugin_api.register_plugin_task(CallbackTransformInTask, config=MobileAppConfig(config))
