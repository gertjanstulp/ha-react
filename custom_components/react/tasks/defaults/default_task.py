
from typing import Dict, Generic, Type, TypeVar
import homeassistant

from homeassistant.core import Event, callback

from ..base import ReactTask
from ...utils.events import EventDataReader
from ...base import ReactBase

# T = TypeVar("T", bound=EventDataReader)

class DefaultTask(ReactTask):

    def __init__(self, react: ReactBase, reader_type: type[EventDataReader] ) -> None:
        super().__init__(react)
        
        self.reader_type = reader_type
        self.readers: Dict[str, EventDataReader] = {}


    @callback
    def async_filter(self, event: Event) -> bool:
        event_reader = self.reader_type(self.react, event)
        if event_reader.applies:
            event_reader.load()
            self.set_reader(event, event_reader)
            return True
        return False


    async def async_execute(self, event: Event) -> None:
        event_reader = self.get_reader(event)
        await self.async_execute_default(event_reader)


    async def async_execute_default(self, event_reader: EventDataReader):
        raise NotImplementedError()


    def set_reader(self, event: Event, reader: EventDataReader):
        self.readers[id(event)] = reader


    def get_reader(self, event: Event) -> EventDataReader:
        return self.readers.get(id(event))
