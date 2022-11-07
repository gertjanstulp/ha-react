from __future__ import annotations


from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import Event

from custom_components.react.base import ReactBase
from custom_components.react.tasks.defaults.default_task import DefaultReactionTask
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.struct import DynamicData
from custom_components.react.const import (
    ATTR_EVENT_MESSAGE, 
    ATTR_LANGUAGE, 
    ATTR_OPTIONS, 
    REACT_ACTION_SPEEK, 
    REACT_TYPE_MEDIA_PLAYER
)

from custom_components.react.plugin.cloud_say.api import Api
from custom_components.react.plugin.cloud_say.const import PLUGIN_NAME


class SpeekTask(DefaultReactionTask):

    def __init__(self, react: ReactBase, api: Api) -> None:
        super().__init__(react, SpeekReactionEvent)
        self.api = api


    async def async_execute_default(self, event: SpeekReactionEvent):
        self.react.log.debug("SpeekTask: speeking with cloud-say")
        await self.api.async_speek(event.create_speek_data(), event.context)


class SpeekReactionEventData(DynamicData):

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.plugin: str = None
        self.message: str = None
        self.options: dict = None
        self.language: str = None

        self.load(source)


class SpeekReactionEvent(ReactionEvent[SpeekReactionEventData]):
    
    def __init__(self, event: Event) -> None:
        super().__init__(event, SpeekReactionEventData)
        

    @property
    def applies(self) -> bool:
        return (
            self.payload.type == REACT_TYPE_MEDIA_PLAYER and
            self.payload.action == REACT_ACTION_SPEEK and 
            self.payload.data.plugin == PLUGIN_NAME
        )


    def create_speek_data(self):
        return {
            ATTR_ENTITY_ID: self.payload.entity,
            ATTR_EVENT_MESSAGE: self.payload.data.message,
            ATTR_OPTIONS: self.payload.data.options,
            ATTR_LANGUAGE: self.payload.data.language,
        }