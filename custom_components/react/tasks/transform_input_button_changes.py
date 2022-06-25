""""Store React data."""
from __future__ import annotations

from homeassistant.core import Event

from ..base import ReactBase
from .transform_base import InputButtonStateData, StateData, StateTransformTask

from ..const import (
    INPUT_BUTTON,
    INPUT_BUTTON_PREFIX,
)


async def async_setup_task(react: ReactBase) -> Task:
    """Set up this task."""
    return Task(react=react)


class Task(StateTransformTask):
    """ "React task base."""
    
    _can_run_disabled = True


    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, INPUT_BUTTON_PREFIX, INPUT_BUTTON)


    def read_state_data(self, event: Event) -> StateData:
        return InputButtonStateData(event.data)