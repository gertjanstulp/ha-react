from __future__ import annotations

from homeassistant.const import (
    EVENT_HOMEASSISTANT_START,
    EVENT_HOMEASSISTANT_STARTED,
    EVENT_HOMEASSISTANT_STOP
)
from homeassistant.core import Event as HassEvent

from custom_components.react.base import ReactBase
from custom_components.react.const import (
    ACTION_SHUTDOWN,
    ACTION_START,
    ACTION_STARTED,
    ENTITY_HASS,
    TYPE_SYSTEM
)
from custom_components.react.tasks.transform_base import EventTransformTask
from custom_components.react.utils.events import ActionEvent, ActionEventPayload


async def async_setup_task(react: ReactBase) -> Task:
    """Set up this task."""
    return Task(react=react)


class Task(EventTransformTask):
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, [EVENT_HOMEASSISTANT_START, EVENT_HOMEASSISTANT_STARTED, EVENT_HOMEASSISTANT_STOP])


    def transform_event_payload(self, hass_event: HassEvent) -> ActionEventPayload:
        result = ActionEventPayload()
        result.entity = ENTITY_HASS
        result.type = TYPE_SYSTEM
        
        if hass_event.event_type == EVENT_HOMEASSISTANT_STARTED:
            result.action = ACTION_STARTED
        elif hass_event.event_type == EVENT_HOMEASSISTANT_START:
            result.action = ACTION_START
        elif hass_event.event_type == EVENT_HOMEASSISTANT_STOP:
            result.action = ACTION_SHUTDOWN
        else:
            raise ValueError()

        return result