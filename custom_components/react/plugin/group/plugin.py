from custom_components.react.plugin.const import PROVIDER_TYPE_NOTIFY
from custom_components.react.plugin.group.const import NOTIFY_PROVIDER_GROUP
from custom_components.react.plugin.group.provider import GroupNotifyProvider
from custom_components.react.plugin.plugin_factory import HassApi, PluginApi
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData


def load(plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
    loader = GroupPluginLoader()
    loader.load(plugin_api, hass_api, config)


class GroupPluginLoader:
    def load(self, plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
        get_react_logger().debug(f"Group plugin: Loading")
        
        plugin_api.register_plugin_provider(
            PROVIDER_TYPE_NOTIFY, 
            NOTIFY_PROVIDER_GROUP, 
            GroupNotifyProvider(plugin_api, hass_api))