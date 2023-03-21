from custom_components.react.plugin.plugin_factory import PluginApi

from custom_components.react.plugin.telegram.api import Api, ApiConfig
from custom_components.react.plugin.telegram.tasks.callback_transform_in_task import CallbackTransformInTask
from custom_components.react.plugin.telegram.tasks.notify_confirm_feedback import NotifyConfirmFeedbackTask
from custom_components.react.plugin.telegram.tasks.notify_send_message_task import NotifySendMessageTask
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData



def load(plugin_api: PluginApi, config: DynamicData):
    get_react_logger().debug(f"Telegram plugin: Loading")
    api = Api(plugin_api.react, ApiConfig(config))

    plugin_api.register_plugin_task(CallbackTransformInTask)

    plugin_api.register_plugin_task(NotifySendMessageTask, api=api)
    plugin_api.register_plugin_task(NotifyConfirmFeedbackTask, api=api)
