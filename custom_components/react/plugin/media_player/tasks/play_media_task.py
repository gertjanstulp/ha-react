from __future__ import annotations

from homeassistant.core import Event

from custom_components.react.base import ReactBase
from custom_components.react.const import REACT_ACTION_PLAY_MEDIA, REACT_TYPE_MEDIA_PLAYER
from custom_components.react.plugin.media_player.api import MediaPlayerApi
from custom_components.react.plugin.media_player.const import PLUGIN_NAME
from custom_components.react.tasks.plugin.base import PluginReactionTask
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData

_LOGGER = get_react_logger()


class MediaPlayerPlayMediaTask(PluginReactionTask):

    def __init__(self, react: ReactBase, api: MediaPlayerApi) -> None:
        super().__init__(react, MediaPlayerPlayMediaReactionEvent)
        self.api = api


    def _debug(self, message: str):
        _LOGGER.debug(f"Input plugin: MediaPlayerPlayMediaTask - {message}")


    async def async_execute_plugin(self, event: MediaPlayerPlayMediaReactionEvent):
        self._debug(f"Setting input_number '{event.payload.entity}'")
        await self.api.async_play_media(
            event.context, 
            event.payload.entity, 
            event.payload.data.media_content_type, 
            event.payload.data.media_content_id)
        

class MediaPlayerPlayMediaReactionEventData(DynamicData):

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.plugin: str = None
        self.media_content_type: str = None
        self.media_content_id: str = None

        self.load(source)


class MediaPlayerPlayMediaReactionEvent(ReactionEvent[MediaPlayerPlayMediaReactionEventData]):
    
    def __init__(self, event: Event) -> None:
        super().__init__(event, MediaPlayerPlayMediaReactionEventData)
        

    @property
    def applies(self) -> bool:
        return (
            self.payload.type == REACT_TYPE_MEDIA_PLAYER and
            self.payload.action == REACT_ACTION_PLAY_MEDIA and 
            self.payload.data and 
            (not self.payload.data.plugin or self.payload.data.plugin == PLUGIN_NAME)
        )
