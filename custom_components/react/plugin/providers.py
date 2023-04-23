from custom_components.react.plugin.plugin_factory import HassApi, PluginApi


class PluginProvider():
    def __init__(self, plugin_api: PluginApi, hass_api: HassApi) -> None:
        self.plugin_api = plugin_api
        self.hass_api = hass_api