from __future__ import annotations

from homeassistant.core import Event
from homeassistant.const import STATE_OFF

from custom_components.react.base import ReactBase
from custom_components.react.const import REACT_TYPE_INPUT_BOOLEAN
from custom_components.react.plugin.input.api import InputApi
from custom_components.react.tasks.plugin.base import PluginReactionTask
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData

_LOGGER = get_react_logger()


class InputBooleanTurnOffTask(PluginReactionTask):

    def __init__(self, react: ReactBase, api: InputApi) -> None:
        super().__init__(react, InputBooleanTurnOffReactionEvent)
        self.api = api


    def _debug(self, message: str):
        _LOGGER.debug(f"Input plugin: InputBooleanTurnOffTask - {message}")


    async def async_execute_plugin(self, event: InputBooleanTurnOffReactionEvent):
        self._debug(f"Turning off input_boolean '{event.payload.entity}'")
        await self.api.async_input_boolean_turn_off(
            event.context, 
            event.payload.entity, 
            event.payload.data.input_provider_name if event.payload.data else None)
        

class InputBooleanTurnOffReactionEventData(DynamicData):

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.input_provider_name: str = None

        self.load(source)


class InputBooleanTurnOffReactionEvent(ReactionEvent[InputBooleanTurnOffReactionEventData]):
    
    def __init__(self, event: Event) -> None:
        super().__init__(event, InputBooleanTurnOffReactionEventData)
        

    @property
    def applies(self) -> bool:
        return (
            self.payload.type == REACT_TYPE_INPUT_BOOLEAN and
            self.payload.action == STATE_OFF
        )
