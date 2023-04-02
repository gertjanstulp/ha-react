from custom_components.react.plugin.notify.api import NotifyApi
from custom_components.react.plugin.notify.config import NotifyConfig
from custom_components.react.plugin.notify.tasks.notify_confirm_feedback_task import NotifyConfirmFeedbackTask
from custom_components.react.plugin.notify.tasks.notify_send_message_task import NotifySendMessageTask
from custom_components.react.plugin.plugin_factory import HassApi, PluginApi
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData


def load(plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
    loader = NotifyPluginLoader()
    loader.load(plugin_api, hass_api, config)


class NotifyPluginLoader:
    def load(self, plugin_api: PluginApi, hass_api: HassApi, config: DynamicData):
        get_react_logger().debug(f"Notify plugin: Loading")

        api = NotifyApi(plugin_api, hass_api, NotifyConfig(config))

        plugin_api.register_plugin_task(NotifySendMessageTask, api=api)
        plugin_api.register_plugin_task(NotifyConfirmFeedbackTask, api=api)
