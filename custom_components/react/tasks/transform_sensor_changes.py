""""Store React data."""
from __future__ import annotations

from homeassistant.core import Event

from ..base import ReactBase
from .transform_base import SensorStateData, StateData, StateTransformTask

from ..const import (
    SENSOR, 
    SENSOR_PREFIX,
)


async def async_setup_task(react: ReactBase) -> Task:
    """Set up this task."""
    return Task(react=react)


class Task(StateTransformTask):
    """ "React task base."""
    
    _can_run_disabled = True


    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, SENSOR_PREFIX, SENSOR)


    def read_state_data(self, event: Event) -> StateData:
        return SensorStateData(event.data)