from homeassistant.components.alarm_control_panel import DOMAIN

from custom_components.react.base import ReactBase
from custom_components.react.plugin.alarm_control_panel.config import AlarmConfig
from custom_components.react.tasks.plugin.base import StateChangeInputBlock, StateChangeData
from custom_components.react.utils.events import StateChangedEvent, StateChangedEventPayload


class AlarmStateChangeData(StateChangeData):
    
    def __init__(self, event_payload: StateChangedEventPayload):
        super().__init__(event_payload)

        if self.old_state_value != self.new_state_value:
            if self.old_state_value != None:
                self.actions.append(f"un_{self.old_state_value}")
            self.actions.append(self.new_state_value)


class AlarmStateChangeInputBlock(StateChangeInputBlock[AlarmConfig]):
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, DOMAIN)


    def read_state_data(self, react_event: StateChangedEvent) -> StateChangeData:
        return AlarmStateChangeData(react_event.payload)
