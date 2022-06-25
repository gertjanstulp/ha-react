""""Store React data."""
from __future__ import annotations

from homeassistant.core import Event

from .transform_base import StateData, StateTransformTask, LightStateData
from ..base import ReactBase

from ..const import (
    LIGHT, 
    LIGHT_PREFIX,
)


async def async_setup_task(react: ReactBase) -> Task:
    """Set up this task."""
    return Task(react=react)


class Task(StateTransformTask):
    """ "React task base."""
    
    _can_run_disabled = True


    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, LIGHT_PREFIX, LIGHT)


    def read_state_data(self, event: Event) -> StateData:
        return LightStateData(event.data)