from typing import Dict

from homeassistant.core import Event, callback

from custom_components.react.base import ReactBase
from custom_components.react.const import EVENT_REACT_ACTION, EVENT_REACT_REACTION
from custom_components.react.tasks.base import ReactTask
from custom_components.react.utils.events import ReactEvent
from custom_components.react.utils.logger import format_data


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


class DefaultReactionTask(DefaultTask):
    def __init__(self, react: ReactBase, e_type: type[ReactEvent]) -> None:
        super().__init__(react, e_type)
        self.events_with_filters = [(EVENT_REACT_REACTION, self.async_filter)]


class DefaultTransformInTask(DefaultTask):
    def __init__(self, react: ReactBase, event_name: str, e_type: type[ReactEvent]) -> None:
        super().__init__(react, e_type)
        self.events_with_filters = [(event_name, self.async_filter)]


    async def async_execute_default(self, action_event: ReactEvent):
        action_event_data = self.create_action_event_data(action_event)
        self.react.log.debug(f"TransformTask: sending action event: {format_data(**action_event_data)}")
        self.react.hass.bus.async_fire(EVENT_REACT_ACTION, action_event_data)
        

    def create_action_event_data(self, source_event: ReactEvent) -> dict:
        raise NotImplementedError()


class DefaultTransformThroughTask(DefaultTask):
    def __init__(self, react: ReactBase, e_type: type[ReactEvent]) -> None:
        super().__init__(react, e_type)
        self.events_with_filters = [(EVENT_REACT_ACTION, self.async_filter)]