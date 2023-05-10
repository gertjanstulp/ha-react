from homeassistant.components.input_button import DOMAIN

from custom_components.react.base import ReactBase
from custom_components.react.const import ACTION_PRESS
from custom_components.react.tasks.plugin.base import StateChangeInputBlock, StateChangeData
from custom_components.react.utils.events import StateChangedEvent, StateChangedEventPayload
from custom_components.react.utils.struct import DynamicData


class InputButtonStateData(StateChangeData):

    def __init__(self, event_payload: StateChangedEventPayload):
        super().__init__(event_payload)

        if self.old_state_value != None and self.new_state_value != None and self.old_state_value != self.new_state_value:
            self.actions.append(ACTION_PRESS)


class InputButtonStateChangeInputBlock(StateChangeInputBlock[DynamicData]):
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, DOMAIN)


    def read_state_data(self, react_event: StateChangedEvent) -> StateChangeData:
        return InputButtonStateData(react_event.payload)
