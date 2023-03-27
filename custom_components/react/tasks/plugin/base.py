from typing import Dict

from homeassistant.core import Event as HassEvent, callback

from custom_components.react.base import ReactBase
from custom_components.react.const import EVENT_REACT_ACTION, EVENT_REACT_REACTION
from custom_components.react.tasks.base import ReactTask, ReactTaskType
from custom_components.react.utils.events import Event
from custom_components.react.utils.logger import format_data, get_react_logger


_LOGGER = get_react_logger()


class PluginTask(ReactTask):

    def __init__(self, react: ReactBase, e_type: type[Event] ) -> None:
        super().__init__(react)
        
        self.e_type = e_type
        self.readers: Dict[str, Event] = {}


    @property
    def task_type(self) -> ReactTaskType:
        return ReactTaskType.PLUGIN


    @callback
    def async_filter(self, hass_event: HassEvent) -> bool:
        action_event = self.e_type(hass_event)
        if action_event.applies:
            self.set_action_event(hass_event, action_event)
            return True
        return False


    async def async_execute(self, hass_event: HassEvent) -> None:
        action_event = self.get_reader(hass_event)
        await self.async_execute_plugin(action_event)


    async def async_execute_plugin(self, event: Event):
        raise NotImplementedError()


    def set_action_event(self, hass_event: HassEvent, reader: Event):
        self.readers[id(hass_event)] = reader


    def get_reader(self, hass_event: HassEvent) -> Event:
        return self.readers.get(id(hass_event))


class PluginReactionTask(PluginTask):
    def __init__(self, react: ReactBase, e_type: type[Event]) -> None:
        super().__init__(react, e_type)
        self.events_with_filters = [(EVENT_REACT_REACTION, self.async_filter)]


class PluginTransformTask(PluginTask):
    def __init__(self, react: ReactBase, event_name: str, e_type: type[Event]) -> None:
        super().__init__(react, e_type)
        self.events_with_filters = [(event_name, self.async_filter)]


    async def async_execute_plugin(self, source_event: Event):
        action_event_payload = self.create_action_event_payload(source_event)
        _LOGGER.debug(f"TransformTask: sending action event: {format_data(**action_event_payload)}")
        self.react.hass.bus.async_fire(EVENT_REACT_ACTION, action_event_payload)
        

    def create_action_event_payload(self, source_event: Event) -> dict:
        raise NotImplementedError()
