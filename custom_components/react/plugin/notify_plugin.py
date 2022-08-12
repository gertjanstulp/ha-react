from __future__ import annotations

from typing import Union

from homeassistant.core import Event, Context

from ..base import ReactBase
from ..utils.events import EventDataReader, ReactionEventDataReader

from ..const import (
    ATTR_EVENT_FEEDBACK_ITEMS,
    ATTR_EVENT_MESSAGE,
    REACT_ACTION_SEND_MESSAGE,
    REACT_TYPE_NOTIFY
)


class NotifyPlugin:
    def __init__(self, react: ReactBase) -> None:
        self.react = react


    @property
    def feedback_event(self):
        raise NotImplementedError()

    
    def get_notify_send_message_reader_type(self) -> type[NotifySendMessageReactionEventDataReader]:
        raise NotImplementedError()


    def get_notify_feedback_reader_type(self) -> type[NotifyFeedbackEventDataReader]:
        raise NotImplementedError()


    async def async_acknowledge_feedback(self, event_reader: NotifyFeedbackEventDataReader):
        raise NotImplementedError()


    async def async_send_notification(self, entity: str, data: dict, context: Context):
        raise NotImplementedError()


class NotifySendMessageReactionEventDataReader(ReactionEventDataReader):
    
    def __init__(self, react: ReactBase, event: Event) -> None:
        super().__init__(react, event)
        
        self.message: Union[str, None] = None
        self.feedback_items_raw: list[dict] = None


    def load(self):
        if self.data:
            self.message = self.data.get(ATTR_EVENT_MESSAGE, None)
            self.feedback_items_raw: list[dict] = self.data.get(ATTR_EVENT_FEEDBACK_ITEMS, None)


    @property
    def applies(self) -> bool:
        return (
            self.type == REACT_TYPE_NOTIFY and
            self.action == REACT_ACTION_SEND_MESSAGE
        )

    
    def create_plugin_data(self) -> dict:
        raise NotImplementedError()


class NotifyFeedbackEventDataReader(EventDataReader):
    
    def __init__(self, react: ReactBase, event: Event) -> None:
        super().__init__(react, event)
        
        self.event_type: Union[str, None] = None
        self.feedback: Union[str, None] = None
        self.acknowledgement: Union[str, None] = None
        self.entity: Union[str, None] = None
