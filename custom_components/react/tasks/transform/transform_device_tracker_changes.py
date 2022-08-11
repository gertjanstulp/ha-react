""""Store React data."""
from __future__ import annotations
from typing import Any

from homeassistant.core import Event

from ..transform_base import NonBinaryStateData, StateData, StateTransformTask

from ...base import ReactBase

from ...const import (
    DEVICE_TRACKER, 
    DEVICE_TRACKER_PREFIX,
)


async def async_setup_task(react: ReactBase) -> Task:
    """Set up this task."""
    return Task(react=react)
     

class DeviceTrackerStateData(NonBinaryStateData):
    
    def __init__(self, event_data: dict[str, Any]):
        super().__init__(DEVICE_TRACKER_PREFIX, event_data)

        if self.old_state_value != self.new_state_value:
            self.actions.append(self.new_state_value)


class Task(StateTransformTask):
    """ "React task base."""

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, DEVICE_TRACKER_PREFIX, DEVICE_TRACKER)
        self.can_run_disabled = True


    def read_state_data(self, event: Event) -> StateData:
        return DeviceTrackerStateData(event.data)