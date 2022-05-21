""""Store React data."""
from __future__ import annotations

from homeassistant.core import Event

from .transform_base import GroupStateData, StateData, StateTransformTask
from ..base import ReactBase

from ..const import (
    GROUP, 
    GROUP_PREFIX,
)


async def async_setup_task(react: ReactBase) -> Task:
    """Set up this task."""
    return Task(react=react)


class Task(StateTransformTask):
    """ "React task base."""
    
    _can_run_disabled = True


    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, GROUP_PREFIX, GROUP)


    def read_state_data(self, event: Event) -> StateData:
        return GroupStateData(event.data)