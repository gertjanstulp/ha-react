from custom_components.react.plugin.const import PROVIDER_TYPE_NOTIFY
from custom_components.react.plugin.mobile_app.const import NOTIFY_PROVIDER_MOBILE_APP
from custom_components.react.plugin.mobile_app.provider import MobileAppProvider
from custom_components.react.plugin.mobile_app.tasks.callback_transform_in_task import CallbackTransformInTask
from custom_components.react.plugin.plugin_factory import HassApi, PluginApi
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData


def load(plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
    loader = MobileAppPluginLoader()
    loader.load(plugin_api, hass_api, config)


class MobileAppPluginLoader:
    def load(self, plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
        get_react_logger().debug(f"Mobile_app plugin: Loading")
        
        plugin_api.register_plugin_provider(
            PROVIDER_TYPE_NOTIFY, 
            NOTIFY_PROVIDER_MOBILE_APP, 
            MobileAppProvider(plugin_api, hass_api))
        
        plugin_api.register_plugin_task(CallbackTransformInTask)
