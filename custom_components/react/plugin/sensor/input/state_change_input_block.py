from homeassistant.components.sensor import DOMAIN

from custom_components.react.base import ReactBase
from custom_components.react.tasks.plugin.base import StateChangeData, StateChangeInputBlock, StateChangeData
from custom_components.react.utils.events import StateChangedEvent
from custom_components.react.utils.struct import DynamicData


class SensorStateChangeInputBlock(StateChangeInputBlock[DynamicData]):
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, DOMAIN)


    def read_state_data(self, react_event: StateChangedEvent) -> StateChangeData:
        return StateChangeData(react_event.payload)
