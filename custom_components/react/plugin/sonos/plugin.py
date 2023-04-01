from custom_components.react.plugin.media_player.const import (
    PLUGIN_NAME as MEDIA_PLAYER_PLUGIN_NAME
)
from custom_components.react.plugin.plugin_factory import PluginApi
from custom_components.react.plugin.sonos.const import SERVICE_TYPE
from custom_components.react.plugin.sonos.service import SonosService
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData


def load(plugin_api: PluginApi, config: DynamicData):
    get_react_logger().debug(f"Telegram plugin: Loading")
    plugin_api.register_plugin_service(MEDIA_PLAYER_PLUGIN_NAME, SERVICE_TYPE, SonosService(plugin_api.react))
