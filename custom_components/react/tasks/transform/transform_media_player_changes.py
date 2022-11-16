""""Store React data."""
from __future__ import annotations

from custom_components.react.base import ReactBase
from custom_components.react.tasks.transform_base import NonBinaryStateData, StateChangedEvent, StateChangedEventPayload, StateData, StateTransformTask
from custom_components.react.const import (
    MEDIAPLAYER, 
    MEDIAPLAYER_PREFIX,
)


async def async_setup_task(react: ReactBase) -> Task:
    """Set up this task."""
    return Task(react=react)


class MediaPlayerStateData(NonBinaryStateData):
    
    def __init__(self, event_payload: StateChangedEventPayload):
        super().__init__(MEDIAPLAYER_PREFIX, event_payload)

        if self.old_state_value != self.new_state_value:
            self.actions.append(self.new_state_value)
            

class Task(StateTransformTask):
    """ "React task base."""

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, MEDIAPLAYER_PREFIX, MEDIAPLAYER)
        self.can_run_disabled = True


    def read_state_data(self, event: StateChangedEvent) -> StateData:
        return MediaPlayerStateData(event.payload)