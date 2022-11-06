from custom_components.react.plugin.plugin_factory import PluginApi

from custom_components.react.plugin.telegram.telegram_api import TelegramApi
from custom_components.react.plugin.telegram.telegram_callback_transform_in_task import TelegramCallbackTransformInTask
from custom_components.react.plugin.telegram.telegram_notify_feedback_confirm_task import TelegramNotifyFeedbackConfirmTask
from custom_components.react.plugin.telegram.telegram_notify_send_message_task import TelegramNotifySendMessageTask


def setup_plugin(api: PluginApi):
    telegram_api = TelegramApi(api.react)

    api.register_default_task(TelegramCallbackTransformInTask)

    api.register_default_task(TelegramNotifySendMessageTask, telegram_api=telegram_api)
    api.register_default_task(TelegramNotifyFeedbackConfirmTask, telegram_api=telegram_api)
