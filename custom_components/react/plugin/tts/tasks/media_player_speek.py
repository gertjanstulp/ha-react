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


class MediaPlayerSpeekTask(DefaultReactionTask):

    def __init__(self, react: ReactBase, api: Api) -> None:
        super().__init__(react, MediaPlayerSpeekReactionEvent)
        self.api = api


    def _debug(self, message: str):
        _LOGGER.debug(f"Tts plugin: MediaPlayerSpeekTask - {message}")


    async def async_execute_default(self, event: MediaPlayerSpeekReactionEvent):
        self._debug("Delivering media_player speek message")
        await self.api.async_media_player_speek( 
            event.payload.entity or None,
            event.payload.data.message,
            event.payload.data.language,
            event.payload.data.options,
            event.context
        )


class MediaPlayerSpeekReactionEventData(DynamicData):

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.plugin: str = None
        self.message: str = None
        self.options: dict = None
        self.language: str = None

        self.load(source)


class MediaPlayerSpeekReactionEvent(ReactionEvent[MediaPlayerSpeekReactionEventData]):
    
    def __init__(self, event: Event) -> None:
        super().__init__(event, MediaPlayerSpeekReactionEventData)
        

    @property
    def applies(self) -> bool:
        return (
            self.payload.type == REACT_TYPE_MEDIA_PLAYER and
            self.payload.action == REACT_ACTION_SPEEK and 
            self.payload.data.plugin == PLUGIN_NAME
        )