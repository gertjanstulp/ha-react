import voluptuous as vol

from custom_components.react.const import CONF_ENTITY_MAPS

from custom_components.react.plugin.const import PROVIDER_TYPE_NOTIFY
from custom_components.react.plugin.factory import InputBlockSetupCallback, PluginSetup, ProviderSetupCallback
from custom_components.react.plugin.mobile_app.config import MobileAppConfig
from custom_components.react.plugin.mobile_app.const import NOTIFY_PROVIDER_MOBILE_APP
from custom_components.react.plugin.mobile_app.provider import MobileAppProvider
from custom_components.react.plugin.mobile_app.input.callback_input_block import CallbackInputBlock

TELEGRAM_PLUGIN_SCHEMA = vol.Schema({
    CONF_ENTITY_MAPS: dict
})


class Setup(PluginSetup[MobileAppConfig]):
    def __init__(self) -> None:
        super().__init__(TELEGRAM_PLUGIN_SCHEMA)


    def setup_config(self, raw_config: dict) -> MobileAppConfig:
        return MobileAppConfig(raw_config)


    def setup_provider(self, setup: ProviderSetupCallback):
        setup(MobileAppProvider, PROVIDER_TYPE_NOTIFY, NOTIFY_PROVIDER_MOBILE_APP)
        

    def setup_input_blocks(self, setup: InputBlockSetupCallback):
        setup(CallbackInputBlock)
