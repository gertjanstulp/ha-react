from homeassistant.const import (
    ATTR_ENTITY_ID
)
from homeassistant.core import Context

from custom_components.react.base import ReactBase
from custom_components.react.const import ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT, ATTR_EVENT_FEEDBACK_ITEM_CONVERSIONATION_ID, ATTR_EVENT_FEEDBACK_ITEM_MESSAGE_ID, ATTR_EVENT_FEEDBACK_ITEM_TEXT, ATTR_EVENT_FEEDBACK_ITEMS, ATTR_EVENT_MESSAGE
from custom_components.react.plugin.notify.api import NotifyApi, NotifyApiConfig
from custom_components.react.plugin.notify.const import PLUGIN_NAME, FeedbackItem
from custom_components.react.plugin.notify.service import NotifyService
from custom_components.react.plugin.notify.tasks.notify_confirm_feedback_task import NotifyConfirmFeedbackTask
from custom_components.react.plugin.notify.tasks.notify_send_message_task import NotifySendMessageTask
from custom_components.react.plugin.plugin_factory import SERVICE_TYPE_DEFAULT, PluginApi
from custom_components.react.utils.struct import DynamicData

from tests.common import TEST_CONTEXT
from tests.tst_context import TstContext


def load(plugin_api: PluginApi, config: DynamicData):
    api = NotifyApi(plugin_api, NotifyApiConfig(config))
    
    plugin_api.register_plugin_task(NotifySendMessageTask, api=api)
    plugin_api.register_plugin_task(NotifyConfirmFeedbackTask, api=api)
    plugin_api.register_plugin_service(PLUGIN_NAME, SERVICE_TYPE_DEFAULT, NotifyServiceMock(plugin_api.react))


class NotifyServiceMock(NotifyService):
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react)


    async def async_notify(self, context: Context, entity_id: str, message: str, feedback_items: list[FeedbackItem]):
        context: TstContext = self.react.hass.data[TEST_CONTEXT]
        context.register_plugin_data({
            ATTR_ENTITY_ID: entity_id,
            ATTR_EVENT_MESSAGE: message,
            ATTR_EVENT_FEEDBACK_ITEMS: ",".join(
                map(lambda x: "|".join([ x.title, x.feedback, x.acknowledgement ]), 
                feedback_items))
        })


    async def async_confirm_feedback(self, context: Context, conversation_id: str, message_id: str, text: str, acknowledgement: str):
        # return await super().async_confirm_feedback(context, conversation_id, message_id, text, acknowledgement)
        context: TstContext = self.react.hass.data[TEST_CONTEXT]
        context.register_plugin_data({
            ATTR_EVENT_FEEDBACK_ITEM_CONVERSIONATION_ID: conversation_id,
            ATTR_EVENT_FEEDBACK_ITEM_MESSAGE_ID: message_id,
            ATTR_EVENT_FEEDBACK_ITEM_TEXT: text,
            ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT: acknowledgement
        })