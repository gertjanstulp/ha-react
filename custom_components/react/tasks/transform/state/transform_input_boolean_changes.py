""""Store React data."""
from __future__ import annotations

from custom_components.react.base import ReactBase
from custom_components.react.tasks.transform.state.base import BinaryStateData, StateChangedEvent, StateData, StateTransformTask
from custom_components.react.const import (
    INPUT_BOOLEAN, 
    INPUT_BOOLEAN_PREFIX,
)


async def async_setup_task(react: ReactBase) -> Task:
    """Set up this task."""
    return Task(react=react)


class Task(StateTransformTask):
    """ "React task base."""

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, INPUT_BOOLEAN_PREFIX, INPUT_BOOLEAN)


    def read_state_data(self, event: StateChangedEvent) -> StateData:
        return BinaryStateData(INPUT_BOOLEAN_PREFIX, event.payload)