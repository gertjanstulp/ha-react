""""Store React data."""
from __future__ import annotations
from typing import Any

from homeassistant.core import Event

from .transform_base import BinaryStateData, StateData, StateTransformTask
from ..base import ReactBase

from ..const import (
    GROUP, 
    GROUP_PREFIX,
)


async def async_setup_task(react: ReactBase) -> Task:
    """Set up this task."""
    return Task(react=react)


class GroupStateData(BinaryStateData):
    def __init__(self, event_data: dict[str, Any]):
        super().__init__(GROUP_PREFIX, event_data)


class Task(StateTransformTask):
    """ "React task base."""
    
    _can_run_disabled = True


    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, GROUP_PREFIX, GROUP)


    def read_state_data(self, event: Event) -> StateData:
        return GroupStateData(event.data)