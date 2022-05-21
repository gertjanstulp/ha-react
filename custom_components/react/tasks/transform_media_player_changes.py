""""Store React data."""
from __future__ import annotations

from homeassistant.core import Event

from .transform_base import MediaPlayerStateData, StateData, StateTransformTask
from ..base import ReactBase

from ..const import (
    MEDIAPLAYER, 
    MEDIAPLAYER_PREFIX,
)


async def async_setup_task(react: ReactBase) -> Task:
    """Set up this task."""
    return Task(react=react)


class Task(StateTransformTask):
    """ "React task base."""
    
    _can_run_disabled = True


    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, MEDIAPLAYER_PREFIX, MEDIAPLAYER)


    def read_state_data(self, event: Event) -> StateData:
        return MediaPlayerStateData(event.data)