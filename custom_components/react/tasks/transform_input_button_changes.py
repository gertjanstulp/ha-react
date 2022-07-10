""""Store React data."""
from __future__ import annotations
from typing import Any

from homeassistant.core import Event

from ..base import ReactBase
from .transform_base import NonBinaryStateData, StateData, StateTransformTask

from ..const import (
    ACTION_PRESS,
    INPUT_BUTTON,
    INPUT_BUTTON_PREFIX,
)


async def async_setup_task(react: ReactBase) -> Task:
    """Set up this task."""
    return Task(react=react)


class InputButtonStateData(NonBinaryStateData):
    def __init__(self, event_data: dict[str, Any]):
        super().__init__(INPUT_BUTTON_PREFIX, event_data)

        if self.old_state_value != None and self.new_state_value != None and self.old_state_value != self.new_state_value:
            self.actions.append(ACTION_PRESS)


class Task(StateTransformTask):
    """ "React task base."""
    
    _can_run_disabled = True


    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, INPUT_BUTTON_PREFIX, INPUT_BUTTON)


    def read_state_data(self, event: Event) -> StateData:
        return InputButtonStateData(event.data)
