from __future__ import annotations
from typing import TYPE_CHECKING

from homeassistant.core import Event, Context

from custom_components.react.base import ReactBase
from custom_components.react.plugin.notify_plugin import NotifyPlugin, NotifySendMessageReactionEventDataReader, NotifyFeedbackEventDataReader

from custom_components.react.const import (
    ATTR_ENTITY,
    ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT,
    ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK,
    ATTR_EVENT_FEEDBACK_ITEMS,
    ATTR_EVENT_MESSAGE, 
)

from tests.common import EVENT_TEST_CALLBACK

if TYPE_CHECKING:
    from tests.tst_context import TstContext


def setup_plugin(react: ReactBase):
    return TestNotifyPlugin(react)


class TestNotifyPlugin(NotifyPlugin):
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react)
        self.notification = None


    def hook_test(self, test_context: TstContext):
        self.test_context = test_context


    @property
    def feedback_event(self):
        return EVENT_TEST_CALLBACK


    def get_notify_send_message_reader_type(self) -> type[NotifySendMessageReactionEventDataReader]:
        return TestNotifySendMessageReactionEventDataReader


    def get_notify_feedback_reader_type(self) -> type[NotifyFeedbackEventDataReader]:
        return TestNotifyFeedbackEventDataReader


    async def async_acknowledge_feedback(self, event_reader: NotifyFeedbackEventDataReader) -> None:
        self.test_context.acknowledge_feedback(event_reader.entity, event_reader.feedback, event_reader.acknowledgement)


    async def async_send_notification(self, entity: str, data: dict, context: Context):
        self.test_context.send_notification(
            entity,
            data,
            context
        )
        

class TestNotifySendMessageReactionEventDataReader(NotifySendMessageReactionEventDataReader):

    def __init__(self, react: ReactBase, event: Event) -> None:
        super().__init__(react, event)


    def create_plugin_data(self) -> dict:
        return {
            ATTR_EVENT_MESSAGE: self.message,
            ATTR_EVENT_FEEDBACK_ITEMS: self.feedback_items_raw,
        }

    
class TestNotifyFeedbackEventDataReader(NotifyFeedbackEventDataReader):
    def __init__(self, react: ReactBase, event: Event) -> None:
        super().__init__(react, event)

        self.event_type = event.event_type


    def load(self):
        self.feedback = self.event.data.get(ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK, None)
        self.entity = self.event.data.get(ATTR_ENTITY, None)
        self.acknowledgement = self.event.data.get(ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT, None)


    def applies(self) -> bool:
        return self.event_type == EVENT_TEST_CALLBACK