from homeassistant.components.input_boolean import DOMAIN

from custom_components.react.base import ReactBase
from custom_components.react.plugin.input_boolean.config import InputBooleanConfig
from custom_components.react.tasks.plugin.base import BinaryStateChangeData, StateChangeInputBlock, StateChangeData
from custom_components.react.utils.events import StateChangedEvent


class InputBooleanStateChangeInputBlock(StateChangeInputBlock[InputBooleanConfig]):
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, DOMAIN)


    def read_state_data(self, react_event: StateChangedEvent) -> StateChangeData:
        return BinaryStateChangeData(react_event.payload)
