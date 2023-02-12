from __future__ import annotations

from homeassistant.components.input_boolean import SERVICE_TOGGLE
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


class InputBooleanToggleTask(DefaultReactionTask):

    def __init__(self, react: ReactBase, api: Api) -> None:
        super().__init__(react, InputBooleanToggleReactionEvent)
        self.api = api


    def _debug(self, message: str):
        _LOGGER.debug(f"Input plugin: InputBooleanToggleTask - {message}")


    async def async_execute_default(self, event: InputBooleanToggleReactionEvent):
        self._debug(f"Toggling input_boolean '{event.payload.entity}'")
        await self.api.async_input_boolean_toggle(event.context, event.payload.entity)
        

class InputBooleanToggleReactionEventData(DynamicData):

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.plugin: str = None

        self.load(source)


class InputBooleanToggleReactionEvent(ReactionEvent[InputBooleanToggleReactionEventData]):
    
    def __init__(self, event: Event) -> None:
        super().__init__(event, InputBooleanToggleReactionEventData)
        

    @property
    def applies(self) -> bool:
        return (
            self.payload.type == REACT_TYPE_INPUT_BOOLEAN and
            self.payload.action == SERVICE_TOGGLE and 
            (not self.payload.data or
             (self.payload.data and (
              (not self.payload.data.plugin or 
               self.payload.data.plugin == PLUGIN_NAME))))
        )
