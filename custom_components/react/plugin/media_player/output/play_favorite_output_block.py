from __future__ import annotations

from homeassistant.core import Event as HaEvent

from custom_components.react.base import ReactBase
from custom_components.react.const import REACT_ACTION_PLAY_FAVORITE, REACT_TYPE_MEDIA_PLAYER
from custom_components.react.plugin.base import ApiType
from custom_components.react.plugin.media_player.api import MediaPlayerApi
from custom_components.react.plugin.media_player.config import MediaPlayerConfig
from custom_components.react.tasks.filters import TYPE_ACTION_REACTION_FILTER_STRATEGY
from custom_components.react.tasks.plugin.base import OutputBlock
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.struct import DynamicData


class MediaPlayerPlayFavoriteOutputBlock(OutputBlock[MediaPlayerConfig], ApiType[MediaPlayerApi]):

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, MediaPlayerPlayFavoriteReactionEvent)

        self.track_reaction_filters=[TYPE_ACTION_REACTION_FILTER_STRATEGY.get_filter(
            REACT_TYPE_MEDIA_PLAYER, 
            REACT_ACTION_PLAY_FAVORITE
        )]


    def log_event_caught(self, react_event: MediaPlayerPlayFavoriteReactionEvent) -> None:
        react_event.session.debug(self.logger, f"Mediaplayer play favorite reaction caught: '{react_event.payload.entity}'")


    async def async_handle_event(self, react_event: MediaPlayerPlayFavoriteReactionEvent):
        await self.api.async_play_favorite(
            react_event.session,
            react_event.context, 
            react_event.payload.entity, 
            react_event.payload.data.favorite_id,
            react_event.payload.data.media_player_provider)
        

class MediaPlayerPlayFavoriteReactionEventData(DynamicData):

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.media_player_provider: str = None
        self.favorite_id: str = None

        self.load(source)


class MediaPlayerPlayFavoriteReactionEvent(ReactionEvent[MediaPlayerPlayFavoriteReactionEventData]):
    
    def __init__(self, ha_event: HaEvent) -> None:
        super().__init__(ha_event, MediaPlayerPlayFavoriteReactionEventData)
        

    @property
    def applies(self) -> bool:
        return self.payload.data
