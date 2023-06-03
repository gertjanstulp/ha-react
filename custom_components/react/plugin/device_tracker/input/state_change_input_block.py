from homeassistant.components.device_tracker import DOMAIN
from homeassistant.const import (
    STATE_HOME,
    STATE_NOT_HOME,
)

from custom_components.react.base import ReactBase
from custom_components.react.tasks.plugin.base import BinaryStateChangeData, StateChangeInputBlock, StateChangeData
from custom_components.react.utils.events import StateChangedEvent
from custom_components.react.utils.struct import DynamicData


class DeviceTrackerStateChangeInputBlock(StateChangeInputBlock[DynamicData]):
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, DOMAIN)


    def read_state_data(self, react_event: StateChangedEvent) -> StateChangeData:
        return BinaryStateChangeData(
            react_event.payload, 
            on_state=STATE_HOME, 
            off_state=STATE_NOT_HOME
        )
