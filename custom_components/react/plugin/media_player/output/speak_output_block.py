from __future__ import annotations

from homeassistant.core import Event as HaEvent

from custom_components.react.base import ReactBase
from custom_components.react.plugin.base import ApiType
from custom_components.react.plugin.media_player.api import MediaPlayerApi
from custom_components.react.plugin.media_player.config import MediaPlayerConfig
from custom_components.react.tasks.filters import TYPE_ACTION_REACTION_FILTER_STRATEGY
from custom_components.react.tasks.plugin.base import OutputBlock
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.struct import DynamicData
from custom_components.react.const import (
    REACT_ACTION_SPEAK, 
    REACT_TYPE_MEDIA_PLAYER
)


class MediaPlayerSpeakOutputBlock(OutputBlock[MediaPlayerConfig], ApiType[MediaPlayerApi]):

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, MediaPlayerSpeakReactionEvent)

        self.track_reaction_filters=[TYPE_ACTION_REACTION_FILTER_STRATEGY.get_filter(
            REACT_TYPE_MEDIA_PLAYER, 
            REACT_ACTION_SPEAK
        )]


    def log_event_caught(self, react_event: MediaPlayerSpeakReactionEvent) -> None:
        react_event.session.debug(self.logger, f"Mediaplayer speak reaction caught: '{react_event.payload.entity}'")


    async def async_handle_event(self, react_event: MediaPlayerSpeakReactionEvent):
        await self.api.async_speak(
            react_event.session,
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


class MediaPlayerSpeakReactionEventData(DynamicData):

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


class MediaPlayerSpeakReactionEvent(ReactionEvent[MediaPlayerSpeakReactionEventData]):
    
    def __init__(self, ha_event: HaEvent) -> None:
        super().__init__(ha_event, MediaPlayerSpeakReactionEventData)
        

    @property
    def applies(self) -> bool:
        return self.payload.data
