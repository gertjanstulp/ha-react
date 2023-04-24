from __future__ import annotations

from homeassistant.core import Event

from custom_components.react.base import ReactBase
from custom_components.react.const import REACT_ACTION_PLAY_FAVORITE, REACT_TYPE_MEDIA_PLAYER
from custom_components.react.plugin.const import PROVIDER_TYPE_MEDIA_PLAYER
from custom_components.react.plugin.media_player.api import MediaPlayerApi
from custom_components.react.tasks.plugin.base import PluginReactionTask
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData

_LOGGER = get_react_logger()


class MediaPlayerPlayFavoriteTask(PluginReactionTask):

    def __init__(self, react: ReactBase, api: MediaPlayerApi) -> None:
        super().__init__(react, MediaPlayerPlayFavoriteReactionEvent)
        self.api = api


    def _debug(self, message: str):
        _LOGGER.debug(f"Mediaplayer plugin: MediaPlayerPlayFavoriteTask - {message}")


    async def async_execute_plugin(self, event: MediaPlayerPlayFavoriteReactionEvent):
        self._debug(f"Playing favorite '{event.payload.data.favorite_id}' on '{event.payload.entity}'")
        await self.api.async_play_favorite(
            event.context, 
            event.payload.entity, 
            event.payload.data.favorite_id,
            event.payload.data.media_player_provider)
        

class MediaPlayerPlayFavoriteReactionEventData(DynamicData):

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.media_player_provider: str = None
        self.favorite_id: str = None

        self.load(source)


class MediaPlayerPlayFavoriteReactionEvent(ReactionEvent[MediaPlayerPlayFavoriteReactionEventData]):
    
    def __init__(self, event: Event) -> None:
        super().__init__(event, MediaPlayerPlayFavoriteReactionEventData)
        

    @property
    def applies(self) -> bool:
        return (
            self.payload.type == REACT_TYPE_MEDIA_PLAYER and
            self.payload.action == REACT_ACTION_PLAY_FAVORITE and
            self.payload.data
        )
