from homeassistant.components.binary_sensor import DOMAIN

from custom_components.react.base import ReactBase
from custom_components.react.tasks.plugin.base import BinaryStateChangeData, StateChangeInputBlock, StateChangeData
from custom_components.react.utils.events import StateChangedEvent
from custom_components.react.utils.struct import DynamicData


class BinarySensorStateChangeInputBlock(StateChangeInputBlock[DynamicData]):
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, DOMAIN)


    def read_state_data(self, react_event: StateChangedEvent) -> StateChangeData:
        return BinaryStateChangeData(react_event.payload)
