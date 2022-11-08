

from homeassistant.core import Context

from custom_components.react.base import ReactBase
from custom_components.react.plugin.plugin_factory import PluginApi
from custom_components.react.plugin.telegram.tasks.notify_send_message_task import NotifySendMessageTask
from custom_components.react.utils.struct import DynamicData
from tests.tst_context import TstContext


def setup_plugin(plugin_api: PluginApi, config: DynamicData):
    plugin_api.register_default_task(NotifySendMessageTaskMock)


class TelegramApiMock():
    def __init__(self, react: ReactBase) -> None:
        self.react = react


    async def async_send_message(self, entity: str, message_data: dict, context: Context):
        context: TstContext = self.react.hass.data["test_context"]
        context.register_notify_send_message(entity, message_data)


class NotifySendMessageTaskMock(NotifySendMessageTask):

    def __init__(self, react: ReactBase) -> None:
        api = TelegramApiMock(react)
        super().__init__(react, api)