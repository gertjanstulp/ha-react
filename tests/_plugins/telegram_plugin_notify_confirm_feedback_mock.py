from homeassistant.core import Context

from custom_components.react.base import ReactBase
from custom_components.react.plugin.plugin_factory import PluginApi
from custom_components.react.plugin.telegram.tasks.notify_confirm_feedback import NotifyConfirmFeedbackTask
from custom_components.react.utils.struct import DynamicData

from tests.tst_context import TstContext


def load(plugin_api: PluginApi, config: DynamicData):
    plugin_api.register_default_task(NotifyConfirmFeedbackTaskMock)


class TelegramApiMock():
    def __init__(self, react: ReactBase) -> None:
        self.react = react

    async def async_confirm_feedback(self, context: Context, feedback_data: dict):
        context: TstContext = self.react.hass.data["test_context"]
        context.register_plugin_data(feedback_data)


class NotifyConfirmFeedbackTaskMock(NotifyConfirmFeedbackTask):

    def __init__(self, react: ReactBase) -> None:
        api = TelegramApiMock(react)
        super().__init__(react, api)