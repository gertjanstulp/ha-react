from __future__ import annotations

from homeassistant.components.input_boolean import SERVICE_TURN_OFF
from homeassistant.core import Event

from custom_components.react.base import ReactBase
from custom_components.react.const import REACT_TYPE_INPUT_BOOLEAN
from custom_components.react.plugin.input.api import Api
from custom_components.react.plugin.input.const import PLUGIN_NAME
from custom_components.react.tasks.defaults.default_task import DefaultReactionTask
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData

_LOGGER = get_react_logger()


class InputBooleanTurnOffTask(DefaultReactionTask):

    def __init__(self, react: ReactBase, api: Api) -> None:
        super().__init__(react, InputBooleanTurnOffReactionEvent)
        self.api = api


    def _debug(self, message: str):
        _LOGGER.debug(f"Input plugin: InputBooleanTurnOffTask - {message}")


    async def async_execute_default(self, event: InputBooleanTurnOffReactionEvent):
        self._debug(f"Turning off input_boolean '{event.payload.entity}'")
        await self.api.async_input_boolean_turn_off(event.context, event.payload.entity)
        

class InputBooleanTurnOffReactionEventData(DynamicData):

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.plugin: str = None

        self.load(source)


class InputBooleanTurnOffReactionEvent(ReactionEvent[InputBooleanTurnOffReactionEventData]):
    
    def __init__(self, event: Event) -> None:
        super().__init__(event, InputBooleanTurnOffReactionEventData)
        

    @property
    def applies(self) -> bool:
        return (
            self.payload.type == REACT_TYPE_INPUT_BOOLEAN and
            self.payload.action == SERVICE_TURN_OFF and 
            self.payload.data and
            self.payload.data.plugin == PLUGIN_NAME
        )
