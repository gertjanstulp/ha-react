
from typing import Union
from homeassistant.core import Event

from ..base import ReactBase

from ..const import (
    ATTR_ACTION,
    ATTR_DATA,
    ATTR_ENTITY,
    ATTR_REACTOR_ID,
    ATTR_TYPE,
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
