from custom_components.react.plugin.const import PROVIDER_TYPE_NOTIFY
from custom_components.react.plugin.factory import PluginBase
from custom_components.react.plugin.group.const import NOTIFY_PROVIDER_GROUP
from custom_components.react.plugin.group.provider import GroupProvider
from custom_components.react.plugin.api import HassApi, PluginApi
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData


class Plugin(PluginBase):
    def load(self, plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
        get_react_logger().debug(f"Group plugin: Loading")
        
        plugin_api.register_plugin_provider(
            PROVIDER_TYPE_NOTIFY, 
            NOTIFY_PROVIDER_GROUP, 
            GroupProvider(plugin_api, hass_api))