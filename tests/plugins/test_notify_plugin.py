from homeassistant.core import Event, Context

from custom_components.react.base import ReactBase
from custom_components.react.plugin.notify_plugin import NotifyPlugin, NotifySendMessageReactionEventDataReader, NotifyFeedbackEventDataReader

from custom_components.react.const import (
    ATTR_CONTEXT,
    ATTR_DATA,
    ATTR_ENTITY, 
    ATTR_TYPE,
    EVENT_REACT_ACTION,
    NEW_STATE,
    OLD_STATE,
    SIGNAL_PROPERTY_COMPLETE,
)
from tests.tst_context import TstContext

EVENT_TEST_CALLBACK = "test_callback"

def setup_plugin(react: ReactBase):
    return TestNotifyPlugin(react)


class TestNotifyPlugin(NotifyPlugin):
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react)
        self.notification = None


    def hook_test(self, test_context: TstContext):
        self.test_context = test_context


    def feedback_event(self):
        return EVENT_TEST_CALLBACK


    def get_notify_send_message_reader_type(self) -> type[NotifySendMessageReactionEventDataReader]:
        return TestNotifySendMessageReactionEventDataReader


    def get_notify_feedback_reader_type(self) -> type[NotifyFeedbackEventDataReader]:
        return TestNotifyFeedbackEventDataReader


    async def async_acknowledge_feedback(self, event_reader: NotifyFeedbackEventDataReader) -> None:
        await super().async_acknowledge_feedback(event_reader)


    async def async_send_notification(self, entity: str, data: dict, context: Context):
        self.test_context.notify(
            entity,
            data,
            context
        )
        

class TestNotifySendMessageReactionEventDataReader(NotifySendMessageReactionEventDataReader):

    def __init__(self, react: ReactBase, event: Event) -> None:
        super().__init__(react, event)


    def create_plugin_data(self) -> dict:
        return {}

    
class TestNotifyFeedbackEventDataReader(NotifyFeedbackEventDataReader):
    def __init__(self, react: ReactBase, event: Event) -> None:
        super().__init__(react, event)


    def load(self):
        pass


    def applies(self) -> bool:
        return self.event_type == EVENT_TEST_CALLBACK