""""Store React data."""
from __future__ import annotations
from typing import Any

from homeassistant.core import Event as HassEvent

from ..transform_base import BinaryStateData, StateData, StateTransformTask

from ...base import ReactBase

from ...const import (
    BINARY_SENSOR, 
    BINARY_SENSOR_PREFIX,
)


async def async_setup_task(react: ReactBase) -> Task:
    """Set up this task."""
    return Task(react=react)


class BinarySensorStateData(BinaryStateData):
    def __init__(self, event_payload: dict[str, Any]):
        super().__init__(BINARY_SENSOR_PREFIX, event_payload)


class Task(StateTransformTask):
    """ "React task base."""

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, BINARY_SENSOR_PREFIX, BINARY_SENSOR)
        self.can_run_disabled = True


    def read_state_data(self, hass_event: HassEvent) -> StateData:
        return BinarySensorStateData(hass_event.data)