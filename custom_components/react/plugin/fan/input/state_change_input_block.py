from numbers import Number
from homeassistant.components.fan import (
    DOMAIN, 
    ATTR_PERCENTAGE,
)
from homeassistant.const import (
    STATE_OFF,
    STATE_ON,
)

from custom_components.react.base import ReactBase
from custom_components.react.const import ACTION_CHANGE, ACTION_DECREASE, ACTION_INCREASE, ACTION_TOGGLE
from custom_components.react.plugin.fan.config import FanConfig
from custom_components.react.tasks.plugin.base import StateChangeInputBlock, StateChangeData
from custom_components.react.utils.events import StateChangedEvent, StateChangedEventPayload


class FanStateChangeData(StateChangeData):
    
    def __init__(self, event_payload: StateChangedEventPayload):
        super().__init__(event_payload)

        if (self.old_state_value == STATE_OFF and self.new_state_value == STATE_ON):
            self.actions.append(STATE_ON)
            self.actions.append(ACTION_TOGGLE)
        if (self.old_state_value == STATE_ON and self.new_state_value == STATE_OFF):
            self.actions.append(STATE_OFF)
            self.actions.append(ACTION_TOGGLE)
        if (self.old_state_value == STATE_ON and self.new_state_value == STATE_ON):
            old_percentage: str = self.old_state_attributes.get(ATTR_PERCENTAGE, None)
            new_percentage: str = self.new_state_attributes.get(ATTR_PERCENTAGE, None)
            if isinstance(old_percentage, Number) and isinstance(new_percentage, Number):
                self.actions.append(ACTION_CHANGE)
                if new_percentage > old_percentage:
                    self.actions.append(ACTION_INCREASE)
                if new_percentage < old_percentage:
                    self.actions.append(ACTION_DECREASE)
        


class FanStateChangeInputBlock(StateChangeInputBlock[FanConfig]):
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, DOMAIN)


    def read_state_data(self, react_event: StateChangedEvent) -> StateChangeData:
        return FanStateChangeData(react_event.payload)
