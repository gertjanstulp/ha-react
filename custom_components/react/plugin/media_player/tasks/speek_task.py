from __future__ import annotations

from homeassistant.core import Event

from custom_components.react.base import ReactBase
from custom_components.react.plugin.media_player.api import MediaPlayerApi
from custom_components.react.tasks.plugin.base import PluginReactionTask
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData
from custom_components.react.const import (
    REACT_ACTION_SPEEK, 
    REACT_TYPE_MEDIA_PLAYER
)


_LOGGER = get_react_logger()


class MediaPlayerSpeekTask(PluginReactionTask):

    def __init__(self, react: ReactBase, api: MediaPlayerApi) -> None:
        super().__init__(react, MediaPlayerSpeekReactionEvent)
        self.api = api


    def _debug(self, message: str):
        _LOGGER.debug(f"Mediaplayer plugin: MediaPlayerSpeekTask - {message}")


    async def async_execute_plugin(self, event: MediaPlayerSpeekReactionEvent):
        self._debug(f"Speeking on mediaplayer '{event.payload.entity}'")
        
        await self.api.async_speek(
            event.context, 
            event.payload.entity,
            event.payload.data.announce,
            event.payload.data.message, 
            event.payload.data.language,
            event.payload.data.volume,
            event.payload.data.wait,
            event.payload.data.cache,
            event.payload.data.options,
            event.payload.data.media_player_provider_name,
            event.payload.data.tts_provider_name,
        )


class MediaPlayerSpeekReactionEventData(DynamicData):

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.announce: bool = None
        self.message: str = None
        self.language: str = None
        self.volume: float = None
        self.wait: int = None
        self.wait: int = None
        self.cache: bool = None
        self.options: DynamicData = None
        self.media_player_provider_name: str = None
        self.tts_provider_name: str = None

        self.load(source)


class MediaPlayerSpeekReactionEvent(ReactionEvent[MediaPlayerSpeekReactionEventData]):
    
    def __init__(self, event: Event) -> None:
        super().__init__(event, MediaPlayerSpeekReactionEventData)
        

    @property
    def applies(self) -> bool:
        return (
            self.payload.type == REACT_TYPE_MEDIA_PLAYER and
            self.payload.action == REACT_ACTION_SPEEK and 
            self.payload.data
        )
