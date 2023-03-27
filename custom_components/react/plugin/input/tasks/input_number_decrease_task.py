from __future__ import annotations

from homeassistant.components.input_number import SERVICE_SET_VALUE
from homeassistant.core import Event

from custom_components.react.base import ReactBase
from custom_components.react.const import REACT_ACTION_DECREASE, REACT_TYPE_INPUT_NUMBER
from custom_components.react.plugin.input.api import InputApi
from custom_components.react.plugin.input.const import PLUGIN_NAME
from custom_components.react.tasks.plugin.base import PluginReactionTask
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData

_LOGGER = get_react_logger()


class InputNumberDecreaseTask(PluginReactionTask):

    def __init__(self, react: ReactBase, api: InputApi) -> None:
        super().__init__(react, InputNumberDecreaseReactionEvent)
        self.api = api


    def _debug(self, message: str):
        _LOGGER.debug(f"Input plugin: InputNumberDecreaseTask - {message}")


    async def async_execute_plugin(self, event: InputNumberDecreaseReactionEvent):
        self._debug(f"Increasing input_number '{event.payload.entity}'")
        await self.api.async_input_number_decrease(event.context, event.payload.entity, event.payload.data.value, event.payload.data.min)
        

class InputNumberDecreaseReactionEventData(DynamicData):

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.plugin: str = None
        self.decrease: float = None
        self.min: float = None

        self.load(source)


class InputNumberDecreaseReactionEvent(ReactionEvent[InputNumberDecreaseReactionEventData]):
    
    def __init__(self, event: Event) -> None:
        super().__init__(event, InputNumberDecreaseReactionEventData)
        

    @property
    def applies(self) -> bool:
        return (
            self.payload.type == REACT_TYPE_INPUT_NUMBER and
            self.payload.action == REACT_ACTION_DECREASE and 
            self.payload.data and 
            (not self.payload.data.plugin or self.payload.data.plugin == PLUGIN_NAME)
        )
