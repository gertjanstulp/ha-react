""""Store React data."""
from __future__ import annotations

from homeassistant.const import STATE_HOME, STATE_NOT_HOME

from custom_components.react.base import ReactBase
from custom_components.react.tasks.transform_base import BinaryStateData, StateChangedEvent, StateData, StateTransformTask
from custom_components.react.const import (
    DEVICE_TRACKER, 
    DEVICE_TRACKER_PREFIX,
)


async def async_setup_task(react: ReactBase) -> Task:
    """Set up this task."""
    return Task(react=react)


class Task(StateTransformTask):
    """ "React task base."""

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, DEVICE_TRACKER_PREFIX, DEVICE_TRACKER)
        self.can_run_disabled = True


    def read_state_data(self, event: StateChangedEvent) -> StateData:
        return BinaryStateData(DEVICE_TRACKER_PREFIX, event.payload, on_state=STATE_HOME, off_state=STATE_NOT_HOME)