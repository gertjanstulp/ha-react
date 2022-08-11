
from typing import Union
from homeassistant.core import Event

from ..base import ReactBase

from ..const import (
    ATTR_ACTION,
    ATTR_ARGS,
    ATTR_DATA,
    ATTR_ENTITY,
    ATTR_EVENT_FEEDBACK_ITEMS,
    ATTR_EVENT_MESSAGE,
    ATTR_REACTOR_ID,
    ATTR_TYPE,
    REACT_ACTION_SEND_MESSAGE,
    REACT_TYPE_NOTIFY,
)


class EventDataReader():
    
    def __init__(self, react: ReactBase, event: Event) -> None:
        self.event = event
        self.react = react
        self.hass_context = event.context


    def load(self):
        pass


    @property
    def applies(self) -> bool:
        raise NotImplementedError()
        

class ReactEventDataReader(EventDataReader):

    def __init__(self, react: ReactBase, event: Event) -> None:
        super().__init__(react, event)

        self.entity = event.data.get(ATTR_ENTITY, None)
        self.type = event.data.get(ATTR_TYPE, None)
        self.action = event.data.get(ATTR_ACTION, None)
        self.data = event.data.get(ATTR_DATA, None)


    def to_dict(self):
        return {
            ATTR_ENTITY: self.entity,
            ATTR_TYPE: self.type,
            ATTR_ACTION: self.action,
            ATTR_DATA: self.data,
        }


class ActionEventDataReader(ReactEventDataReader):

    def __init__(self, react: ReactBase, event: Event) -> None:
        super().__init__(react, event)


class ReactionEventDataReader(ReactEventDataReader):

    def __init__(self, react: ReactBase, event: Event) -> None:
        super().__init__(react, event)
       
        self.reactor_id =  event.data.get(ATTR_REACTOR_ID, None)


class NotifySendMessageReactionEventDataReader(ReactionEventDataReader):
    
    def __init__(self, react: ReactBase, event: Event) -> None:
        super().__init__(react, event)
        
        self.message: Union[str, None] = None
        self.inline_keyboard: Union[str, None] = None


    def load(self):
        if self.data:
            self.message = self.data.get(ATTR_EVENT_MESSAGE, None)
            feedback_items_raw: list[dict] = self.data.get(ATTR_EVENT_FEEDBACK_ITEMS, None)
            if feedback_items_raw:
                self.inline_keyboard = ", ".join(
                    map(lambda x: " ".join([
                        f"{x.title}:/react", 
                        x.command, 
                        x.acknowledgement
                    ]), 
                    feedback_items_raw)
                )


    @property
    def applies(self) -> bool:
        return (
            self.type == REACT_TYPE_NOTIFY and
            self.action == REACT_ACTION_SEND_MESSAGE
        )


class NotifyFeedbackEventDataReader(EventDataReader):
    
    def __init__(self, react: ReactBase, event: Event) -> None:
        super().__init__(react, event)
        
        self.event_type: Union[str, None] = None
        self.telegram_command: Union[str, None] = None
        self.command: Union[str, None] = None
        self.acknowledgement: Union[str, None] = None
        self.entity: Union[str, None] = None
