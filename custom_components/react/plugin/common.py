from typing import Generic, Type, TypeVar

from homeassistant.core import Event

from custom_components.react.utils.events import ReactEvent, ReactionEvent, ReactionEventData
from custom_components.react.const import ATTR_EVENT_FEEDBACK_ITEMS, REACT_ACTION_SEND_MESSAGE, REACT_TYPE_NOTIFY
from custom_components.react.utils.struct import DynamicData


class NotifySendMessageReactionEventFeedbackItem(DynamicData):
    def __init__(self, source: dict = None) -> None:
        super().__init__()

        self.title: str = None
        self.feedback: str = None
        self.acknowledgement: str = None

        self.load(source)


class NotifySendMessageReactionEventNotificationData(DynamicData):
    type_hints: dict = { ATTR_EVENT_FEEDBACK_ITEMS: NotifySendMessageReactionEventFeedbackItem }

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.message: str = None
        self.feedback_items: list[NotifySendMessageReactionEventFeedbackItem] = None

        self.load(source)


    def create_service_data(self) -> dict:
        raise NotImplementedError()


T_sd = TypeVar('T_sd', bound=NotifySendMessageReactionEventNotificationData)
class NotifySendMessageReactionEventData(ReactionEventData[T_sd], Generic[T_sd]):
    def __init__(self, t_sd_type: Type[T_sd] = NotifySendMessageReactionEventNotificationData) -> None:
        super().__init__(t_sd_type)


T_s = TypeVar('T_s', bound=NotifySendMessageReactionEventData)
class NotifySendMessageReactionEvent(ReactionEvent[T_s], Generic[T_s]):
    
    def __init__(self, event: Event, s_type: Type[T_s] = NotifySendMessageReactionEventData[T_sd]) -> None:
        super().__init__(event, s_type)
        

    @property
    def applies(self) -> bool:
        return (
            self.data.type == REACT_TYPE_NOTIFY and
            self.data.action == REACT_ACTION_SEND_MESSAGE
        )


# class NotifyFeedbackReactionEventData(ReactionEventData[T_sd], Generic[T_sd]):
#     def __init__(self) -> None:
#         super().__init__()
        
#         self.feedback: str = None
#         self.acknowledgement: str = None
#         self.entity: str = None


# T_f = TypeVar('T_f', bound=NotifyFeedbackReactionEventData)
# class NotifyFeedbackReactionEvent(ReactEvent[T_f], Generic[T_f]):
    
#     def __init__(self, event: Event, f_type: Type[T_f] = NotifyFeedbackReactionEventData) -> None:
#         super().__init__(event, f_type)


#     @property
#     def applies(self) -> bool:
#         return (
#             self.data.type == REACT_TYPE_NOTIFY and
#             self.data.action == REACT_ACTION_SEND_MESSAGE
#         )