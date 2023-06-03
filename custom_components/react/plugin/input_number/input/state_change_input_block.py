from homeassistant.components.input_number import DOMAIN

from custom_components.react.base import ReactBase
from custom_components.react.plugin.input_number.config import InputNumberConfig
from custom_components.react.tasks.plugin.base import StateChangeInputBlock, StateChangeData
from custom_components.react.utils.events import StateChangedEvent


class InputNumberStateChangeInputBlock(StateChangeInputBlock[InputNumberConfig]):
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, DOMAIN)


    def read_state_data(self, react_event: StateChangedEvent) -> StateChangeData:
        return StateChangeData(react_event.payload)
