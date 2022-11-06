from __future__ import annotations


from homeassistant.const import Platform, ATTR_ENTITY_ID
from homeassistant.core import Event

from custom_components.react.base import ReactBase
from custom_components.react.const import ATTR_EVENT_MESSAGE
from custom_components.react.tasks.defaults.default_task import DefaultReactionTask
from custom_components.react.utils.events import ReactionEvent
from custom_components.react.utils.struct import DynamicData

from custom_components.react.plugin.cloud_say.plugin import PLUGIN_NAME


async def async_setup_task(react: ReactBase) -> SpeekTask:
    """Set up this task."""
    return SpeekTask(react=react)


class SpeekTask(DefaultReactionTask):

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, CloudSaySpeekReactionEvent)


    async def async_execute_default(self, action_event: CloudSaySpeekReactionEvent):
        await self.react.hass.services.async_call(
            Platform.TTS, 
            "cloud_say",
            action_event.data.data.create_service_data(action_event.data.entity),
            action_event.context)


class CloudSaySpeekReactionEventData(DynamicData):

    def __init__(self, source: dict) -> None:
        super().__init__()
        
        self.plugin: str = None
        self.message: str = None
        self.options: dict = None
        self.language: str = None
        self.load(source)


    def create_service_data(self, entity: str):
        return {
            ATTR_ENTITY_ID: entity,
            ATTR_EVENT_MESSAGE: self.message,
            ATTR_OPTIONS: self.options,
            ATTR_LANGUAGE: self.language,
        }


class CloudSaySpeekReactionEvent(ReactionEvent[CloudSaySpeekReactionEventData]):
    
    def __init__(self, event: Event) -> None:
        super().__init__(event, CloudSaySpeekReactionEventData)
        

    @property
    def applies(self) -> bool:
        return (
            self.payload.type == REACT_TYPE_MEDIA_PLAYER and
            self.payload.action == REACT_ACTION_SPEEK and 
            self.payload.data.plugin == PLUGIN_NAME
        )