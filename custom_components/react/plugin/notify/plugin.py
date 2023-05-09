import voluptuous as vol

from homeassistant.helpers import config_validation as cv

from custom_components.react.plugin.factory import PluginBase
from custom_components.react.plugin.notify.api import NotifyApi
from custom_components.react.plugin.notify.config import NotifyConfig
from custom_components.react.plugin.notify.const import ATTR_NOTIFY_PROVIDER
from custom_components.react.plugin.notify.tasks.notify_confirm_feedback_task import NotifyConfirmFeedbackTask
from custom_components.react.plugin.notify.tasks.notify_send_message_task import NotifySendMessageTask
from custom_components.react.plugin.api import HassApi, PluginApi
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData


NOTIFY_PLUGIN_CONFIG_SCHEMA = vol.Schema({
    vol.Optional(ATTR_NOTIFY_PROVIDER) : cv.string,
})


class Plugin(PluginBase):
    def __init__(self) -> None:
        super().__init__(NOTIFY_PLUGIN_CONFIG_SCHEMA)


    def load(self, plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
        get_react_logger().debug(f"Notify plugin: Loading")

        api = NotifyApi(plugin_api, hass_api, NotifyConfig(config))

        plugin_api.register_plugin_task(NotifySendMessageTask, api=api)
        plugin_api.register_plugin_task(NotifyConfirmFeedbackTask, api=api)
