from __future__ import annotations

from homeassistant.components.input_number import SERVICE_SET_VALUE
from homeassistant.core import Event

from custom_components.react.base import ReactBase
from custom_components.react.const import REACT_TYPE_INPUT_NUMBER
from custom_components.react.plugin.input.api import Api
from custom_components.react.plugin.input.const import PLUGIN_NAME
from custom_components.react.tasks.defaults.default_task import DefaultReactionTask
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData

_LOGGER = get_react_logger()


class InputNumberSetTask(DefaultReactionTask):

    def __init__(self, react: ReactBase, api: Api) -> None:
        super().__init__(react, InputNumberSetReactionEvent)
        self.api = api


    def _debug(self, message: str):
        _LOGGER.debug(f"Input plugin: InputNumberSetTask - {message}")


    async def async_execute_default(self, event: InputNumberSetReactionEvent):
        self._debug(f"Setting input_number '{event.payload.entity}'")
        await self.api.async_input_number_set(event.context, event.payload.entity, event.payload.data.value)
        

class InputNumberSetReactionEventData(DynamicData):

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.plugin: str = None
        self.value: float = None

        self.load(source)


class InputNumberSetReactionEvent(ReactionEvent[InputNumberSetReactionEventData]):
    
    def __init__(self, event: Event) -> None:
        super().__init__(event, InputNumberSetReactionEventData)
        

    @property
    def applies(self) -> bool:
        return (
            self.payload.type == REACT_TYPE_INPUT_NUMBER and
            self.payload.action == SERVICE_SET_VALUE and 
            self.payload.data.plugin == PLUGIN_NAME
        )
