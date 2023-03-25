from custom_components.react.plugin.notify.api import NotifyApi, NotifyApiConfig
from custom_components.react.plugin.notify.tasks.notify_confirm_feedback_task import NotifyConfirmFeedbackTask
from custom_components.react.plugin.notify.tasks.notify_send_message_task import NotifySendMessageTask
from custom_components.react.plugin.plugin_factory import PluginApi
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData


def load(plugin_api: PluginApi, config: DynamicData):
    get_react_logger().debug(f"Notify plugin: Loading")
    api = NotifyApi(plugin_api, NotifyApiConfig(config))

    plugin_api.register_plugin_task(NotifySendMessageTask, api=api)
    plugin_api.register_plugin_task(NotifyConfirmFeedbackTask, api=api)
