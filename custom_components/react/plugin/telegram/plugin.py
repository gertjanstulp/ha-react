from custom_components.react.plugin.plugin_factory import PluginApi

from custom_components.react.plugin.telegram.api import Api
from custom_components.react.plugin.telegram.tasks.callback_transform_in_task import CallbackTransformInTask
from custom_components.react.plugin.telegram.tasks.notify_confirm_feedback import NotifyConfirmFeedbackTask
from custom_components.react.plugin.telegram.tasks.notify_send_message_task import NotifySendMessageTask



def setup_plugin(plugin_api: PluginApi):
    api = Api(plugin_api.react)

    plugin_api.register_default_task(CallbackTransformInTask)

    plugin_api.register_default_task(NotifySendMessageTask, api=api)
    plugin_api.register_default_task(NotifyConfirmFeedbackTask, api=api)
