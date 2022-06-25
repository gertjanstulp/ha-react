""""Store React data."""
from __future__ import annotations

from homeassistant.core import Event

from ..base import ReactBase
from .transform_base import AlarmStateData, StateData, StateTransformTask

from ..const import (
    ALARM,
    ALARM_PREFIX,
)


async def async_setup_task(react: ReactBase) -> Task:
    """Set up this task."""
    return Task(react=react)


class Task(StateTransformTask):
    """ "React task base."""
    
    _can_run_disabled = True


    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, ALARM_PREFIX, ALARM)


    def read_state_data(self, event: Event) -> StateData:
        return AlarmStateData(event.data)