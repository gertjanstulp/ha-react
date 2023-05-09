from custom_components.react.plugin.const import PROVIDER_TYPE_NOTIFY
from custom_components.react.plugin.factory import PluginBase
from custom_components.react.plugin.persistent_notification.const import NOTIFY_PROVIDER_PERSISTENT_NOTIFICATION
from custom_components.react.plugin.persistent_notification.provider import PersistentNotificationProvider
from custom_components.react.plugin.persistent_notification.tasks.dismiss_transform_in_task import DismissTransformInTask
from custom_components.react.plugin.api import HassApi, PluginApi
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData


class Plugin(PluginBase):
    def load(self, plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
        get_react_logger().debug(f"Persistent notification plugin: Loading")
        
        plugin_api.register_plugin_provider(
            PROVIDER_TYPE_NOTIFY, 
            NOTIFY_PROVIDER_PERSISTENT_NOTIFICATION, 
            PersistentNotificationProvider(plugin_api, hass_api))
        
        plugin_api.register_plugin_task(DismissTransformInTask)
