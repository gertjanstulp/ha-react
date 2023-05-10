from custom_components.react.plugin.browser_mod.provider import BrowserModProvider
from custom_components.react.plugin.browser_mod.const import MEDIA_PLAYER_BROWSER_MOD_PROVIDER
from custom_components.react.plugin.const import PROVIDER_TYPE_MEDIA_PLAYER
from custom_components.react.plugin.factory import PluginSetup, ProviderSetupCallback
from custom_components.react.utils.struct import DynamicData


class Setup(PluginSetup[DynamicData]):
    def setup_provider(self, setup: ProviderSetupCallback):
        setup(
            BrowserModProvider,
            PROVIDER_TYPE_MEDIA_PLAYER, 
            MEDIA_PLAYER_BROWSER_MOD_PROVIDER, 
        )
