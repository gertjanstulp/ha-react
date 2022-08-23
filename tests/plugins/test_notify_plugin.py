from __future__ import annotations
from typing import TYPE_CHECKING

from homeassistant.core import Event, Context

from custom_components.react.base import ReactBase
from custom_components.react.plugin.notify_plugin import NotifyPlugin, NotifySendMessageReactionEventDataReader, NotifyFeedbackEventDataReader

from custom_components.react.const import (
    ATTR_ACTION,
    ATTR_DATA,
    ATTR_ENTITY,
    ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT,
    ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK,
    ATTR_EVENT_FEEDBACK_ITEM_TITLE,
    ATTR_EVENT_FEEDBACK_ITEMS,
    ATTR_EVENT_MESSAGE,
    ATTR_TYPE,
    REACT_ACTION_FEEDBACK,
    REACT_TYPE_NOTIFY, 
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


    async def async_send_notification(self, entity: str, notification_data: dict, context: Context):
        self.test_context.send_notification(
            entity,
            notification_data,
            context
        )


    async def async_acknowledge_feedback(self, feedback_data: dict, context: Context):
        self.test_context.acknowledge_feedback(feedback_data)
        

class TestNotifySendMessageReactionEventDataReader(NotifySendMessageReactionEventDataReader):

    def __init__(self, react: ReactBase, event: Event) -> None:
        super().__init__(react, event)


    def create_service_data(self) -> dict:
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


    def create_action_event_data(self) -> dict:
        return {
            ATTR_ENTITY: self.entity,
            ATTR_TYPE: REACT_TYPE_NOTIFY,
            ATTR_ACTION: REACT_ACTION_FEEDBACK,
            ATTR_DATA: {
                ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK: self.feedback
            }
        }


    def create_feedback_data(self) -> dict:
        return {
            ATTR_ENTITY: self.entity,
            ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT: self.acknowledgement,
            ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK: self.feedback
            # ATTR_MESSAGEID: self.message_id,
            # ATTR_CHAT_ID: self.chat_id,
            # ATTR_MESSAGE: escape_markdown(f"{self.message_text} - {self.acknowledgement}"),
            # ATTR_KEYBOARD_INLINE: None
        }