
from typing import Dict

from homeassistant.core import Event, callback

from ..base import ReactTask
from ...utils.events import ReactEvent
from ...base import ReactBase


class DefaultTask(ReactTask):

    def __init__(self, react: ReactBase, e_type: type[ReactEvent] ) -> None:
        super().__init__(react)
        
        self.e_type = e_type
        self.readers: Dict[str, ReactEvent] = {}


    @callback
    def async_filter(self, event: Event) -> bool:
        action_event = self.e_type(event)
        if action_event.applies:
            self.set_action_event(event, action_event)
            return True
        return False


    async def async_execute(self, event: Event) -> None:
        action_event = self.get_reader(event)
        await self.async_execute_default(action_event)


    async def async_execute_default(self, action_event: ReactEvent):
        raise NotImplementedError()


    def set_action_event(self, event: Event, reader: ReactEvent):
        self.readers[id(event)] = reader


    def get_reader(self, event: Event) -> ReactEvent:
        return self.readers.get(id(event))
