""""Store React data."""
from __future__ import annotations
from typing import Any

from homeassistant.core import Event

from ..base import ReactBase
from .transform_base import NonBinaryStateData, StateData, StateTransformTask

from ..const import (
    ACTION_CHANGE,
    SENSOR, 
    SENSOR_PREFIX,
)


async def async_setup_task(react: ReactBase) -> Task:
    """Set up this task."""
    return Task(react=react)
        

class SensorStateData(NonBinaryStateData):
    def __init__(self, event_data: dict[str, Any]):
        super().__init__(SENSOR_PREFIX, event_data)

        if self.new_state_value != self.old_state_value:
            self.actions.append(ACTION_CHANGE)
            

class Task(StateTransformTask):
    """ "React task base."""
    
    _can_run_disabled = True


    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, SENSOR_PREFIX, SENSOR)


    def read_state_data(self, event: Event) -> StateData:
        return SensorStateData(event.data)