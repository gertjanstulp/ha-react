from custom_components.react.plugin.const import PROVIDER_TYPE_CLIMATE
from custom_components.react.plugin.factory import PluginSetup, ProviderSetupCallback
from custom_components.react.plugin.ramses.const import CLIMATE_RAMSES_PROVIDER
from custom_components.react.plugin.ramses.provider import RamsesProvider
from custom_components.react.utils.struct import DynamicData


class Setup(PluginSetup[DynamicData]):

    def setup_provider(self, setup: ProviderSetupCallback):
        setup(RamsesProvider, PROVIDER_TYPE_CLIMATE, CLIMATE_RAMSES_PROVIDER)
