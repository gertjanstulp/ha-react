from __future__ import annotations

from homeassistant.components.input_text import SERVICE_SET_VALUE
from homeassistant.core import Event

from custom_components.react.base import ReactBase
from custom_components.react.const import REACT_TYPE_INPUT_TEXT
from custom_components.react.plugin.input.api import InputApi
from custom_components.react.tasks.plugin.base import PluginReactionTask
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData

_LOGGER = get_react_logger()


class InputTextSetTask(PluginReactionTask):

    def __init__(self, react: ReactBase, api: InputApi) -> None:
        super().__init__(react, InputTextSetReactionEvent)
        self.api = api


    def _debug(self, message: str):
        _LOGGER.debug(f"Input plugin: InputTextSetTask - {message}")


    async def async_execute_plugin(self, event: InputTextSetReactionEvent):
        self._debug(f"Setting input_text '{event.payload.entity}'")
        await self.api.async_input_text_set(
            event.context, 
            event.payload.entity, 
            event.payload.data.value, 
            event.payload.data.input_provider)
        

class InputTextSetReactionEventData(DynamicData):

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.input_provider: str = None
        self.value: float = None

        self.load(source)


class InputTextSetReactionEvent(ReactionEvent[InputTextSetReactionEventData]):
    
    def __init__(self, event: Event) -> None:
        super().__init__(event, InputTextSetReactionEventData)
        

    @property
    def applies(self) -> bool:
        return (
            self.payload.type == REACT_TYPE_INPUT_TEXT and
            self.payload.action == SERVICE_SET_VALUE and
            self.payload.data
        )
