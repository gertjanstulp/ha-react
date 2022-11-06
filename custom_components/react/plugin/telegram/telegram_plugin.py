from custom_components.react.plugin.plugin_api import PluginApi
from custom_components.react.plugin.telegram.telegram_callback_transform_in_task import TelegramCallbackTransformInTask
from custom_components.react.plugin.telegram.telegram_notify_send_message_task import TelegramNotifySendMessageTask


def setup_plugin(api: PluginApi):
    api.register_default_task(TelegramNotifySendMessageTask)
    api.register_default_task(TelegramCallbackTransformInTask)

