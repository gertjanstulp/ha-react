""""Store React data."""
from __future__ import annotations
from typing import Any

from homeassistant.core import Event

from ..base import ReactBase
from .transform_base import NonBinaryStateData, StateData, StateTransformTask

from ..const import (
    ALARM,
    ALARM_PREFIX,
)


async def async_setup_task(react: ReactBase) -> Task:
    """Set up this task."""
    return Task(react=react)


class AlarmStateData(NonBinaryStateData):
    def __init__(self, event_data: dict[str, Any]):
        super().__init__(ALARM_PREFIX, event_data)

        if self.old_state_value != self.new_state_value:
            if self.old_state_value != None:
                self.actions.append(f"un_{self.old_state_value}")
            self.actions.append(self.new_state_value)


class Task(StateTransformTask):
    """ "React task base."""
    
    _can_run_disabled = True


    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, ALARM_PREFIX, ALARM)


    def read_state_data(self, event: Event) -> StateData:
        return AlarmStateData(event.data)