from custom_components.react.plugin.const import PROVIDER_TYPE_MEDIA_PLAYER
from custom_components.react.plugin.plugin_factory import HassApi, PluginApi
from custom_components.react.plugin.sonos.const import MEDIA_PLAYER_SONOS_PROVIDER
from custom_components.react.plugin.sonos.provider import SonosProvider
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData


def load(plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
    loader = SonosPluginLoader()
    loader.load(plugin_api, hass_api, config)


class SonosPluginLoader:
    def load(self, plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
        get_react_logger().debug(f"Sonos plugin: Loading")

        plugin_api.register_plugin_provider(
            PROVIDER_TYPE_MEDIA_PLAYER, 
            MEDIA_PLAYER_SONOS_PROVIDER, 
            SonosProvider(plugin_api, hass_api))
