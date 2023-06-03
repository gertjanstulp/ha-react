from custom_components.react.plugin.const import PROVIDER_TYPE_MEDIA_PLAYER
from custom_components.react.plugin.factory import PluginSetup, ProviderSetupCallback
from custom_components.react.plugin.sonos.const import MEDIA_PLAYER_SONOS_PROVIDER
from custom_components.react.plugin.sonos.provider import SonosProvider
from custom_components.react.utils.struct import DynamicData


class Setup(PluginSetup[DynamicData]):
    def setup_provider(self, setup: ProviderSetupCallback):
        setup(SonosProvider, PROVIDER_TYPE_MEDIA_PLAYER, MEDIA_PLAYER_SONOS_PROVIDER)
    