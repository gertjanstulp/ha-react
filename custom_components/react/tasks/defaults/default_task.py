
from typing import Dict, Generic, Type, TypeVar
import homeassistant

from homeassistant.core import Event, callback

from ..base import ReactTask
from ...utils.events import EventDataReader
from ...base import ReactBase

T = TypeVar("T", bound=EventDataReader)

class DefaultTask(ReactTask, Generic[T]):

    def __init__(self, react: ReactBase, cls: Type[T]) -> None:
        super().__init__(react)
        
        self.cls = cls
        self.readers: Dict[str, T] = {}


    @callback
    def async_filter(self, event: Event) -> bool:
        event_reader = self.cls(self.react, event)
        if event_reader.applies:
            event_reader.load()
            self.set_reader(event, event_reader)
            return True
        return False


    async def async_execute(self, event: Event) -> None:
        event_reader = self.get_reader(event)
        await self.async_execute_default(event_reader)


    async def async_execute_default(self, event_reader: T):
        raise NotImplementedError()


    def set_reader(self, event: Event, reader: T):
        self.readers[id(event)] = reader


    def get_reader(self, event: Event) -> T:
        return self.readers.get(id(event))
