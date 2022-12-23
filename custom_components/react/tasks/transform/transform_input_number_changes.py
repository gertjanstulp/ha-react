""""Store React data."""
from __future__ import annotations

from custom_components.react.base import ReactBase
from custom_components.react.tasks.transform_base import NonBinaryStateData, StateChangedEvent, StateChangedEventPayload, StateData, StateTransformTask
from custom_components.react.const import (
    ACTION_CHANGE,
    INPUT_NUMBER, 
    INPUT_NUMBER_PREFIX,
)


async def async_setup_task(react: ReactBase) -> Task:
    """Set up this task."""
    return Task(react=react)
        

class InputNumberStateData(NonBinaryStateData):
    
    def __init__(self, event_payload: StateChangedEventPayload):
        super().__init__(INPUT_NUMBER_PREFIX, event_payload)

        if self.new_state_value != self.old_state_value:
            self.actions.append(ACTION_CHANGE)
            

class Task(StateTransformTask):
    """ "React task base."""

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, INPUT_NUMBER_PREFIX, INPUT_NUMBER)
        self.can_run_disabled = True


    def read_state_data(self, event: StateChangedEvent) -> StateData:
        return InputNumberStateData(event.payload)