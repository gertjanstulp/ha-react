from __future__ import annotations

from homeassistant.core import Event

from custom_components.react.base import ReactBase
from custom_components.react.const import REACT_ACTION_INCREASE, REACT_TYPE_INPUT_NUMBER
from custom_components.react.plugin.input.api import InputApi
from custom_components.react.tasks.plugin.base import PluginReactionTask
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData

_LOGGER = get_react_logger()


class InputNumberIncreaseTask(PluginReactionTask):

    def __init__(self, react: ReactBase, api: InputApi) -> None:
        super().__init__(react, InputNumberIncreaseReactionEvent)
        self.api = api


    def _debug(self, message: str):
        _LOGGER.debug(f"Input plugin: InputNumberIncreaseTask - {message}")


    async def async_execute_plugin(self, event: InputNumberIncreaseReactionEvent):
        self._debug(f"Increasing input_number '{event.payload.entity}'")
        await self.api.async_input_number_increase(
            event.context, 
            event.payload.entity, 
            event.payload.data.value, 
            event.payload.data.max, 
            event.payload.data.input_provider_name)
        

class InputNumberIncreaseReactionEventData(DynamicData):

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.input_provider_name: str = None
        self.value: float = None
        self.max: float = None

        self.load(source)


class InputNumberIncreaseReactionEvent(ReactionEvent[InputNumberIncreaseReactionEventData]):
    
    def __init__(self, event: Event) -> None:
        super().__init__(event, InputNumberIncreaseReactionEventData)
        

    @property
    def applies(self) -> bool:
        return (
            self.payload.type == REACT_TYPE_INPUT_NUMBER and
            self.payload.action == REACT_ACTION_INCREASE and
            self.payload.data
        )
