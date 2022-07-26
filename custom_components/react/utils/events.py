
from dataclasses import dataclass
from ntpath import join
from typing import Union
from homeassistant.core import Event

from ..const import (
    ATTR_ACTION,
    ATTR_DATA,
    ATTR_ENTITY,
    ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT,
    ATTR_EVENT_FEEDBACK_ITEM_COMMAND,
    ATTR_EVENT_FEEDBACK_ITEM_TITLE,
    ATTR_EVENT_FEEDBACK_ITEMS,
    ATTR_EVENT_MESSAGE,
    ATTR_REACTOR_ID,
    ATTR_TYPE,
    REACT_ACTION_SEND_MESSAGE,
    REACT_TYPE_NOTIFY,
)

EVENT_READER_PROP = "event_reader"

class ReactEventDataReader():
    entity: Union[str, None] = None
    type: Union[str, None] = None
    action: Union[str, None] = None
    data: Union[dict, None] = None

    def __init__(self, event: Event) -> None:
        self.event = event

        self.entity = event.data.get(ATTR_ENTITY, None)
        self.type = event.data.get(ATTR_TYPE, None)
        self.action = event.data.get(ATTR_ACTION, None)
        self.data = event.data.get(ATTR_DATA, None)
        self.context = event.context


class ActionEventDataReader(ReactEventDataReader):
    def __init__(self, event: Event) -> None:
        super().__init__(event)


class ReactionEventDataReader(ReactEventDataReader):
    def __init__(self, event: Event) -> None:
        super().__init__(event)
        self.reactor_id =  event.data.get(ATTR_REACTOR_ID, None)


class NotifySendMessageReactionEventDataReader(ReactionEventDataReader):
    message: Union[str, None] = None
    inline_keyboard: Union[str, None] = None


    def __init__(self, event: Event) -> None:
        super().__init__(event)

        if self.data:
            self.message = self.data.get(ATTR_EVENT_MESSAGE, None)
            feedback_items_raw: list[dict] = self.data.get(ATTR_EVENT_FEEDBACK_ITEMS, None)
            if feedback_items_raw:
                self.inline_keyboard = ", ".join(
                    map(lambda x: " ".join([
                        f"{x.get(ATTR_EVENT_FEEDBACK_ITEM_TITLE, None)}:/react" , 
                        x.get(ATTR_EVENT_FEEDBACK_ITEM_COMMAND, None), 
                        x.get(ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT, None)
                    ]), 
                    feedback_items_raw)
                )


    @property
    def applies(self) -> bool:
        return (
            self.type == REACT_TYPE_NOTIFY and
            self.action == REACT_ACTION_SEND_MESSAGE and
            self.message
        )