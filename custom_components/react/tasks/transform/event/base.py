
from typing import Union

from homeassistant.core import Event as HassEvent

from custom_components.react.base import ReactBase
from custom_components.react.const import EVENT_REACT_ACTION
from custom_components.react.tasks.base import ReactTask, ReactTaskType
from custom_components.react.utils.events import ActionEventPayload


class EventTransformTask(ReactTask):
    def __init__(self, react: ReactBase, event_names: Union[str, list[str]]) -> None:
        super().__init__(react)

        if isinstance(event_names, str):
            event_names = [event_names]
        self.event_types = event_names


    @property
    def task_type(self) -> ReactTaskType:
        return ReactTaskType.RUNTIME

    
    def transform_event_payload(self, hass_event: HassEvent) -> ActionEventPayload:
        raise NotImplementedError()

    
    async def async_execute(self, hass_event: HassEvent) -> None:
        payload = self.transform_event_payload(hass_event)
        self.react.hass.bus.async_fire(EVENT_REACT_ACTION, payload)