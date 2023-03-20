""""Store React data."""
from __future__ import annotations

from custom_components.react.base import ReactBase
from custom_components.react.tasks.transform.state.base import BinaryStateData, StateChangedEvent, StateData, StateTransformTask
from custom_components.react.const import (
    BINARY_SENSOR, 
    BINARY_SENSOR_PREFIX,
)


async def async_setup_task(react: ReactBase) -> Task:
    """Set up this task."""
    return Task(react=react)


class Task(StateTransformTask):
    """ "React task base."""

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, BINARY_SENSOR_PREFIX, BINARY_SENSOR)


    def read_state_data(self, event: StateChangedEvent) -> StateData:
        return BinaryStateData(BINARY_SENSOR_PREFIX, event.payload)