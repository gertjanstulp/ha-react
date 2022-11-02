from __future__ import annotations
from typing import TYPE_CHECKING

from homeassistant.core import Event, Context

from custom_components.react.base import ReactBase
from custom_components.react.plugin.notify_plugin import NotifyFeedbackEventData, NotifyPlugin, NotifySendMessageReactionEvent, NotifyFeedbackEvent, NotifySendMessageReactionEventData, NotifySendMessageReactionEventNotificationData

from custom_components.react.const import (
    ATTR_ACTION,
    ATTR_DATA,
    ATTR_ENTITY,
    ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT,
    ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK,
    ATTR_EVENT_FEEDBACK_ITEMS,
    ATTR_EVENT_MESSAGE,
    ATTR_TYPE,
    REACT_ACTION_FEEDBACK,
    REACT_TYPE_NOTIFY, 
)
from custom_components.react.utils.struct import DynamicData

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


    def get_notify_send_message_event_type(self) -> type[NotifySendMessageReactionEvent]:
        return TestNotifySendMessageReactionEvent


    def get_notify_feedback_event_type(self) -> type[NotifyFeedbackEvent]:
        return TestNotifyFeedbackEvent


    async def async_send_notification(self, entity: str, notification_data: dict, context: Context):
        self.test_context.send_notification(
            entity,
            notification_data,
            context
        )


    async def async_acknowledge_feedback(self, feedback_data: dict, context: Context):
        self.test_context.acknowledge_feedback(feedback_data)


class TestNotifySendMessageReactionEventNotificationData(NotifySendMessageReactionEventNotificationData):
    def __init__(self, source: dict) -> None:
        super().__init__(source)


    def create_service_data(self) -> dict:
        return self.as_dict()
    

class TestNotifySendMessageReactionEventData(NotifySendMessageReactionEventData[TestNotifySendMessageReactionEventNotificationData]):
    def __init__(self) -> None:
        super().__init__(TestNotifySendMessageReactionEventNotificationData)


class TestNotifySendMessageReactionEvent(NotifySendMessageReactionEvent[TestNotifySendMessageReactionEventData]):

    def __init__(self, event: Event) -> None:
        super().__init__(event, TestNotifySendMessageReactionEventData)


class TestNotifyFeedbackEvent(NotifyFeedbackEventData):
    def __init__(self) -> None:
        super().__init__()

    
class TestNotifyFeedbackEvent(NotifyFeedbackEvent[NotifyFeedbackEventData]):
    def __init__(self, event: Event) -> None:
        super().__init__(event)

        self.event_type = event.event_type


    def applies(self) -> bool:
        return self.event_type == EVENT_TEST_CALLBACK


    def create_action_event_data(self, react: ReactBase) -> dict:
        return {
            ATTR_ENTITY: self.data.entity,
            ATTR_TYPE: REACT_TYPE_NOTIFY,
            ATTR_ACTION: REACT_ACTION_FEEDBACK,
            ATTR_DATA: {
                ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK: self.data.feedback
            }
        }


    def create_feedback_data(self, react: ReactBase) -> dict:
        return {
            ATTR_ENTITY: self.data.entity,
            ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT: self.data.acknowledgement,
            ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK: self.data.feedback
        }