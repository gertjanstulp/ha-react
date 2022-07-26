from __future__ import annotations
from typing import Dict, TypedDict

from homeassistant.const import ATTR_COMMAND, Platform
from homeassistant.core import Event, callback

from ..base import ReactTask

from ...base import ReactBase
from ...utils.events import NotifySendMessageReactionEventDataReader, ReactionEventDataReader

from ...const import (
     ATTR_DATA,
     ATTR_EVENT_MESSAGE,
     ATTR_SERVICE_DATA_INLINE_KEYBOARD,
     EVENT_REACT_REACTION
)

async def async_setup_task(react: ReactBase) -> Task:
    """Set up this task."""
    return Task(react=react)


class Task(ReactTask):

    readers: Dict[str, NotifySendMessageReactionEventDataReader] = {}

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react)
        self.events_with_filters = [(EVENT_REACT_REACTION, self.async_filter)]


    @callback
    def async_filter(self, event: Event) -> bool:
        event_reader = NotifySendMessageReactionEventDataReader(event)
        if event_reader.applies:
            self.readers[id(event)] = event_reader
            return True
        return False


    async def async_execute(self, event: Event) -> None:
        event_reader = self.readers.get(id(event))
        notify_data = {
            ATTR_EVENT_MESSAGE: event_reader.message,
        }
        if event_reader.inline_keyboard:
            notify_data[ATTR_DATA] = {
                ATTR_SERVICE_DATA_INLINE_KEYBOARD : event_reader.inline_keyboard
            }
        await self.react.hass.services.async_call(
            Platform.NOTIFY, 
            event_reader.entity,
            notify_data, 
            context=event_reader.context)
        test = 1
