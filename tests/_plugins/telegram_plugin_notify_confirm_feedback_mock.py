from homeassistant.core import Context

from custom_components.react.base import ReactBase
from custom_components.react.plugin.plugin_factory import PluginApi
from custom_components.react.plugin.telegram.tasks.notify_confirm_feedback import NotifyConfirmFeedbackTask

from tests.tst_context import TstContext


def setup_plugin(plugin_api: PluginApi):
    plugin_api.register_default_task(NotifyConfirmFeedTaskMock)


class TelegramApiMock():
    def __init__(self, react: ReactBase) -> None:
        self.react = react

    async def async_confirm_feedback(self, feedback_data: dict, context: Context):
        context: TstContext = self.react.hass.data["test_context"]
        context.register_notify_confirm_feedback(feedback_data)


class NotifyConfirmFeedTaskMock(NotifyConfirmFeedbackTask):

    def __init__(self, react: ReactBase) -> None:
        api = TelegramApiMock(react)
        super().__init__(react, api)