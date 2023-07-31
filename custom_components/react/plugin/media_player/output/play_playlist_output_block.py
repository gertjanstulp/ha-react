from __future__ import annotations

from homeassistant.core import Event as HaEvent

from custom_components.react.base import ReactBase
from custom_components.react.const import REACT_ACTION_PLAY_PLAYLIST, REACT_TYPE_MEDIA_PLAYER
from custom_components.react.plugin.base import ApiType
from custom_components.react.plugin.media_player.api import MediaPlayerApi
from custom_components.react.plugin.media_player.config import MediaPlayerConfig
from custom_components.react.tasks.filters import TYPE_ACTION_REACTION_FILTER_STRATEGY
from custom_components.react.tasks.plugin.base import OutputBlock
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.struct import DynamicData


class MediaPlayerPlayPlaylistOutputBlock(OutputBlock[MediaPlayerConfig], ApiType[MediaPlayerApi]):

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, MediaPlayerPlayPlaylistReactionEvent)

        self.track_reaction_filters=[TYPE_ACTION_REACTION_FILTER_STRATEGY.get_filter(
            REACT_TYPE_MEDIA_PLAYER, 
            REACT_ACTION_PLAY_PLAYLIST
        )]


    async def async_handle_event(self, react_event: MediaPlayerPlayPlaylistReactionEvent):
        react_event.session.debug(self.logger, f"Mediaplayer play playlist reaction caught: '{react_event.payload.entity}'")
        await self.api.async_play_playlist(
            react_event.session,
            react_event.context, 
            react_event.payload.entity, 
            react_event.payload.data.playlist_id,
            react_event.payload.data.media_player_provider)
        

class MediaPlayerPlayPlaylistReactionEventData(DynamicData):

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.media_player_provider: str = None
        self.playlist_id: str = None

        self.load(source)


class MediaPlayerPlayPlaylistReactionEvent(ReactionEvent[MediaPlayerPlayPlaylistReactionEventData]):
    
    def __init__(self, ha_event: HaEvent) -> None:
        super().__init__(ha_event, MediaPlayerPlayPlaylistReactionEventData)
        

    @property
    def applies(self) -> bool:
        return self.payload.data
