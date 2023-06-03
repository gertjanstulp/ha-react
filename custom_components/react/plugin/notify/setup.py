import voluptuous as vol

from homeassistant.helpers import config_validation as cv

from custom_components.react.plugin.factory import ApiSetupCallback, OutputBlockSetupCallback, PluginSetup
from custom_components.react.plugin.notify.api import NotifyApi
from custom_components.react.plugin.notify.config import NotifyConfig
from custom_components.react.plugin.notify.const import ATTR_NOTIFY_PROVIDER, NOTIFY_RESOLVER_KEY
from custom_components.react.plugin.notify.output.confirm_feedback_output_block import NotifyConfirmFeedbackOutputBlock
from custom_components.react.plugin.notify.output.send_message_output_block import NotifySendMessageOutputBlock
from custom_components.react.plugin.notify.resolver import NotifyPluginResolver


NOTIFY_PLUGIN_CONFIG_SCHEMA = vol.Schema({
    vol.Optional(ATTR_NOTIFY_PROVIDER) : cv.string,
})


class Setup(PluginSetup[NotifyConfig]):
    def __init__(self) -> None:
        super().__init__(NOTIFY_PLUGIN_CONFIG_SCHEMA)


    def setup(self):
        self.plugin.hass_api.hass_set_data(NOTIFY_RESOLVER_KEY, NotifyPluginResolver())
    

    def setup_config(self, raw_config: dict) -> NotifyConfig:
        return NotifyConfig(raw_config)

    
    def setup_api(self, setup: ApiSetupCallback):
        setup(NotifyApi)
    

    def setup_output_blocks(self, setup: OutputBlockSetupCallback):
        setup(
            [
                NotifySendMessageOutputBlock,
                NotifyConfirmFeedbackOutputBlock,
            ],
        )
    