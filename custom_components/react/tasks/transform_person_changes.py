""""Store React data."""
from __future__ import annotations
from typing import Any

from homeassistant.core import Event

from .transform_base import NonBinaryStateData, StateData, StateTransformTask
from ..base import ReactBase

from ..const import (
    PERSON, 
    PERSON_PREFIX,
)


async def async_setup_task(react: ReactBase) -> Task:
    """Set up this task."""
    return Task(react=react)


class PersonStateData(NonBinaryStateData):
    def __init__(self, event_data: dict[str, Any]):
        super().__init__(PERSON_PREFIX, event_data)

        if self.old_state_value != self.new_state_value:
            self.actions.append(self.new_state_value)


class Task(StateTransformTask):
    """ "React task base."""
    
    _can_run_disabled = True


    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, PERSON_PREFIX, PERSON)


    def read_state_data(self, event: Event) -> StateData:
        return PersonStateData(event.data)
