from custom_components.react.plugin.media_player.provider import MediaPlayerProvider
from custom_components.react.plugin.api import HassApi, PluginApi


class BrowserModProvider(MediaPlayerProvider):
    def __init__(self, plugin_api: PluginApi, hass_api: HassApi) -> None:
        super().__init__(plugin_api, hass_api)


    @property
    def support_announce(self) -> bool:
        return True
