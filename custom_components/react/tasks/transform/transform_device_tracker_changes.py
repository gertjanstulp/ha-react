""""Store React data."""
from __future__ import annotations
from typing import Any
from homeassistant.const import STATE_HOME, STATE_NOT_HOME, STATE_ON

from homeassistant.core import Event as HassEvent

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
    
    def __init__(self, event_payload: dict[str, Any]):
        super().__init__(DEVICE_TRACKER_PREFIX, event_payload)
        
        if self.old_state_value == STATE_NOT_HOME and self.new_state_value == STATE_HOME:
            self.actions.append(STATE_HOME)
        elif self.old_state_value == STATE_HOME and self.new_state_value == STATE_NOT_HOME:
            self.actions.append(STATE_NOT_HOME)


class Task(StateTransformTask):
    """ "React task base."""

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, DEVICE_TRACKER_PREFIX, DEVICE_TRACKER)
        self.can_run_disabled = True


    def read_state_data(self, hass_event: HassEvent) -> StateData:
        return DeviceTrackerStateData(hass_event.data)