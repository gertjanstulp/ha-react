from __future__ import annotations
from asyncio import sleep


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
        self._debug(f"Speeking on mediaplayer '{event.payload.entity}'")
        
        if not self.api.verify_config():
            return

        if event.payload.data.interrupt_service:
            await self.api.async_media_player_interrupt(event.context, event.payload.entity, event.payload.data.interrupt_service)
        if event.payload.data.volume:
            await self.api.async_media_player_set_volume(event.context, event.payload.entity, event.payload.data.volume)
        await self.api.async_say(event.context, event.payload.entity, event.payload.data.message, event.payload.data.language, event.payload.data.options)
        if event.payload.data.wait:
            await self.api.async_wait(event.payload.data.wait)
        if event.payload.data.resume_service:
            await self.api.async_media_player_resume(event.context, event.payload.entity, event.payload.data.resume_service)


class MediaPlayerSpeekReactionEventData(DynamicData):

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.plugin: str = None
        self.message: str = None
        self.options: DynamicData = None
        self.language: str = None
        self.volume: float = None
        self.interrupt_service: str = None
        self.resume_service: str = None
        self.wait: int = None

        self.load(source)


class MediaPlayerSpeekReactionEvent(ReactionEvent[MediaPlayerSpeekReactionEventData]):
    
    def __init__(self, event: Event) -> None:
        super().__init__(event, MediaPlayerSpeekReactionEventData)
        

    @property
    def applies(self) -> bool:
        return (
            self.payload.type == REACT_TYPE_MEDIA_PLAYER and
            self.payload.action == REACT_ACTION_SPEEK and 
            (not self.payload.data.plugin or self.payload.data.plugin == PLUGIN_NAME)
        )