from __future__ import annotations

from homeassistant.core import Event as HaEvent

from custom_components.react.base import ReactBase
from custom_components.react.plugin.base import ApiType
from custom_components.react.plugin.media_player.api import MediaPlayerApi
from custom_components.react.plugin.media_player.config import MediaPlayerConfig
from custom_components.react.tasks.filters import TYPE_ACTION_REACTION_FILTER_STRATEGY
from custom_components.react.tasks.plugin.base import OutputBlock
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData
from custom_components.react.const import (
    REACT_ACTION_SPEEK, 
    REACT_TYPE_MEDIA_PLAYER
)


_LOGGER = get_react_logger()


class MediaPlayerSpeekOutputBlock(OutputBlock[MediaPlayerConfig], ApiType[MediaPlayerApi]):

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, MediaPlayerSpeekReactionEvent)

        self.track_reaction_filters=[TYPE_ACTION_REACTION_FILTER_STRATEGY.get_filter(
            REACT_TYPE_MEDIA_PLAYER, 
            REACT_ACTION_SPEEK
        )]


    def _debug(self, message: str):
        _LOGGER.debug(f"Mediaplayer plugin: MediaPlayerSpeekOutputBlock - {message}")


    async def async_handle_event(self, react_event: MediaPlayerSpeekReactionEvent):
        self._debug(f"Speeking on mediaplayer '{react_event.payload.entity}'")
        
        await self.api.async_speek(
            react_event.context, 
            react_event.payload.entity,
            react_event.payload.data.announce,
            react_event.payload.data.message, 
            react_event.payload.data.language,
            react_event.payload.data.volume,
            react_event.payload.data.wait,
            react_event.payload.data.cache,
            react_event.payload.data.options,
            react_event.payload.data.media_player_provider,
            react_event.payload.data.tts_provider,
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
        self.media_player_provider: str = None
        self.tts_provider: str = None

        self.load(source)


class MediaPlayerSpeekReactionEvent(ReactionEvent[MediaPlayerSpeekReactionEventData]):
    
    def __init__(self, ha_event: HaEvent) -> None:
        super().__init__(ha_event, MediaPlayerSpeekReactionEventData)
        

    @property
    def applies(self) -> bool:
        return self.payload.data
