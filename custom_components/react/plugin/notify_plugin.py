from __future__ import annotations

from typing import Generic, Type, TypeVar
from custom_components.react.plugin.common import NotifySendMessageReactionEvent

from homeassistant.core import Event, Context
from custom_components.react.base import ReactBase
from custom_components.react.utils.events import ReactEvent, ReactionEvent, ReactionEventData
from custom_components.react.utils.struct import DynamicData

from custom_components.react.const import (
    ATTR_EVENT_FEEDBACK_ITEMS, 
    REACT_ACTION_SEND_MESSAGE, 
    REACT_TYPE_NOTIFY
)


class NotifyPlugin:
    def __init__(self, react: ReactBase) -> None:
        self.react = react


    @property
    def feedback_event(self):
        raise NotImplementedError()

    
    def get_notify_send_message_event_type(self) -> type[NotifySendMessageReactionEvent]:
        raise NotImplementedError()


    def get_notify_feedback_event_type(self) -> type[NotifyFeedbackEvent]:
        raise NotImplementedError()


    async def async_send_notification(self, entity: str, notification_data: dict, context: Context):
        raise NotImplementedError()


    async def async_acknowledge_feedback(self, feedback_data: dict, context: Context):
        raise NotImplementedError()


# class NotifySendMessageReactionEventFeedbackItem(DynamicData):
#     def __init__(self, source: dict = None) -> None:
#         super().__init__()

#         self.title: str = None
#         self.feedback: str = None
#         self.acknowledgement: str = None

#         self.load(source)


# class NotifySendMessageReactionEventNotificationData(DynamicData):
#     type_hints: dict = { ATTR_EVENT_FEEDBACK_ITEMS: NotifySendMessageReactionEventFeedbackItem }

#     def __init__(self, source: dict) -> None:
#         super().__init__()
        
#         self.message: str = None
#         self.feedback_items: list[NotifySendMessageReactionEventFeedbackItem] = None

#         self.load(source)


#     def create_service_data(self) -> dict:
#         raise NotImplementedError()


# T_sd = TypeVar('T_sd', bound=NotifySendMessageReactionEventNotificationData)
# class NotifySendMessageReactionEventData(ReactionEventData[T_sd], Generic[T_sd]):
#     def __init__(self, t_sd_type: Type[T_sd] = NotifySendMessageReactionEventNotificationData) -> None:
#         super().__init__(t_sd_type)


# T_s = TypeVar('T_s', bound=NotifySendMessageReactionEventData)
# class NotifySendMessageReactionEvent(ReactionEvent[T_s], Generic[T_s]):
    
#     def __init__(self, event: Event, s_type: Type[T_s] = NotifySendMessageReactionEventData[T_sd]) -> None:
#         super().__init__(event, s_type)
        

#     @property
#     def applies(self) -> bool:
#         return (
#             self.data.type == REACT_TYPE_NOTIFY and
#             self.data.action == REACT_ACTION_SEND_MESSAGE
#         )


# class NotifyFeedbackEventData(DynamicData):
#     def __init__(self) -> None:
#         super().__init__()
        
#         self.feedback: str = None
#         self.acknowledgement: str = None
#         self.entity: str = None


# T_f = TypeVar('T_f', bound=NotifyFeedbackEventData)
# class NotifyFeedbackEvent(ReactEvent[T_f], Generic[T_f]):
    
#     def __init__(self, event: Event, f_type: Type[T_f] = NotifyFeedbackEventData) -> None:
#         super().__init__(event, f_type)

    
#     def create_action_event_data(self, react: ReactBase) -> dict:
#         raise NotImplementedError()


#     def create_feedback_data(self, react: ReactBase) -> dict:
#         raise NotImplementedError()