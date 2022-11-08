from __future__ import annotations


from homeassistant.core import Event

from custom_components.react.base import ReactBase
from custom_components.react.tasks.defaults.default_task import DefaultReactionTask
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData
from custom_components.react.const import (
    REACT_ACTION_SPEEK, 
    REACT_TYPE_MEDIA_PLAYER
)

from custom_components.react.plugin.tts.api import Api
from custom_components.react.plugin.tts.const import PLUGIN_NAME

_LOGGER = get_react_logger()


class SpeekTask(DefaultReactionTask):

    def __init__(self, react: ReactBase, api: Api) -> None:
        super().__init__(react, SpeekReactionEvent)
        self.api = api


    def _debug(self, message: str):
        _LOGGER.debug(f"Tts plugin: Speektask - {message}")


    async def async_execute_default(self, event: SpeekReactionEvent):
        self._debug("Delivering tts speek message")
        await self.api.async_speek( 
            event.payload.entity or None,
            event.payload.data.message,
            event.payload.data.options,
            event.payload.data.language,
            event.context
        )


class SpeekReactionEventData(DynamicData):

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.plugin: str = None
        self.message: str = None
        self.options: dict = None
        self.language: str = None

        self.load(source)


class SpeekReactionEvent(ReactionEvent[SpeekReactionEventData]):
    
    def __init__(self, event: Event) -> None:
        super().__init__(event, SpeekReactionEventData)
        

    @property
    def applies(self) -> bool:
        return (
            self.payload.type == REACT_TYPE_MEDIA_PLAYER and
            self.payload.action == REACT_ACTION_SPEEK and 
            self.payload.data.plugin == PLUGIN_NAME
        )