from homeassistant.core import Context

from custom_components.react.base import ReactBase
from custom_components.react.const import ATTR_ENTITY
from custom_components.react.plugin.plugin_factory import PluginApi
from custom_components.react.plugin.telegram.const import ATTR_MESSAGE_DATA
from custom_components.react.plugin.telegram.tasks.notify_send_message_task import NotifySendMessageTask
from custom_components.react.utils.struct import DynamicData
from tests.common import TEST_CONTEXT
from tests.tst_context import TstContext


def load(plugin_api: PluginApi, config: DynamicData):
    plugin_api.register_plugin_task(NotifySendMessageTaskMock)


class TelegramApiMock():
    def __init__(self, react: ReactBase) -> None:
        self.react = react


    async def async_send_message(self, context: Context, entity: str, message_data: dict):
        context: TstContext = self.react.hass.data[TEST_CONTEXT]
        context.register_plugin_data({
            ATTR_ENTITY: entity,
            ATTR_MESSAGE_DATA: message_data
        })


class NotifySendMessageTaskMock(NotifySendMessageTask):

    def __init__(self, react: ReactBase) -> None:
        api = TelegramApiMock(react)
        super().__init__(react, api)