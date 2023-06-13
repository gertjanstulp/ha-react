from __future__ import annotations

from homeassistant.core import Event as HaEvent

from custom_components.react.base import ReactBase
from custom_components.react.const import REACT_ACTION_PAUSE, REACT_ACTION_PLAY_FAVORITE, REACT_TYPE_MEDIA_PLAYER
from custom_components.react.plugin.base import ApiType
from custom_components.react.plugin.media_player.api import MediaPlayerApi
from custom_components.react.plugin.media_player.config import MediaPlayerConfig
from custom_components.react.tasks.filters import TYPE_ACTION_REACTION_FILTER_STRATEGY
from custom_components.react.tasks.plugin.base import OutputBlock
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.struct import DynamicData


class MediaPlayerPauseOutputBlock(OutputBlock[MediaPlayerConfig], ApiType[MediaPlayerApi]):

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, MediaPlayerPauseReactionEvent)

        self.track_reaction_filters=[TYPE_ACTION_REACTION_FILTER_STRATEGY.get_filter(
            REACT_TYPE_MEDIA_PLAYER, 
            REACT_ACTION_PAUSE,
        )]


    def log_event_caught(self, react_event: MediaPlayerPauseReactionEvent) -> None:
        react_event.session.debug(self.logger, f"Mediaplayer pause reaction caught: '{react_event.payload.entity}'")


    async def async_handle_event(self, react_event: MediaPlayerPauseReactionEvent):
        await self.api.async_pause(
            react_event.session,
            react_event.context, 
            react_event.payload.entity,
            react_event.payload.data.media_player_provider if react_event.payload.data else None,
        )
        

class MediaPlayerPauseReactionEventData(DynamicData):

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.media_player_provider: str = None

        self.load(source)


class MediaPlayerPauseReactionEvent(ReactionEvent[MediaPlayerPauseReactionEventData]):
    
    def __init__(self, ha_event: HaEvent) -> None:
        super().__init__(ha_event, MediaPlayerPauseReactionEventData)
        

    @property
    def applies(self) -> bool:
        return self.payload.data
