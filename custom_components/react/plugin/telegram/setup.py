import voluptuous as vol

from custom_components.react.const import CONF_ENTITY_MAPS
from custom_components.react.plugin.const import PROVIDER_TYPE_NOTIFY
from custom_components.react.plugin.factory import InputBlockSetupCallback, PluginSetup, ProviderSetupCallback
from custom_components.react.plugin.telegram.config import TelegramConfig
from custom_components.react.plugin.telegram.const import NOTIFY_PROVIDER_TELEGRAM
from custom_components.react.plugin.telegram.provider import TelegramProvider
from custom_components.react.plugin.telegram.input.callback_input_block import CallbackInputBlock

TELEGRAM_PLUGIN_SCHEMA = vol.Schema({
    CONF_ENTITY_MAPS: dict
})


class Setup(PluginSetup[TelegramConfig]):
    def __init__(self) -> None:
        super().__init__(TELEGRAM_PLUGIN_SCHEMA)

    
    def setup_config(self, raw_config: dict) -> TelegramConfig:
        return TelegramConfig(raw_config)
    

    def setup_provider(self, setup: ProviderSetupCallback):
        setup(TelegramProvider, PROVIDER_TYPE_NOTIFY, NOTIFY_PROVIDER_TELEGRAM)


    def setup_input_blocks(self, setup: InputBlockSetupCallback):
        setup(CallbackInputBlock)
