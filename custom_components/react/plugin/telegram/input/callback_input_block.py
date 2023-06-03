from __future__ import annotations

from homeassistant.core import Event as HaEvent
from homeassistant.components.telegram_bot import (
    ATTR_MESSAGE, 
    EVENT_TELEGRAM_CALLBACK, 
)
from custom_components.react.plugin.telegram.config import TelegramConfig
from custom_components.react.plugin.telegram.const import NOTIFY_PROVIDER_TELEGRAM
from custom_components.react.tasks.filters import EVENT_TYPE_FILTER_STRATEGY

from custom_components.react.utils.events import ReactEvent
from custom_components.react.base import ReactBase
from custom_components.react.tasks.plugin.base import EventInputBlock
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData
from custom_components.react.const import (
    ATTR_ACTION, 
    ATTR_DATA, 
    ATTR_ENTITY, 
    ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT,
    ATTR_EVENT_FEEDBACK_ITEM_CONVERSIONATION_ID,
    ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK,
    ATTR_EVENT_FEEDBACK_ITEM_MESSAGE_ID,
    ATTR_EVENT_FEEDBACK_ITEM_TEXT, 
    ATTR_EVENT_NOTIFY_PROVIDER, 
    ATTR_TYPE, 
    EVENTPAYLOAD_COMMAND_REACT, 
    ATTR_EVENT_NOTIFY_PROVIDER_PAYLOAD, 
    REACT_ACTION_FEEDBACK_RETRIEVED, 
    REACT_TYPE_NOTIFY
)


_LOGGER = get_react_logger()


class CallbackInputBlock(EventInputBlock[TelegramConfig]):
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, CallbackActionEvent)
        
        self.track_event_filters = [EVENT_TYPE_FILTER_STRATEGY.get_filter(EVENT_TELEGRAM_CALLBACK)]


    def load(self):
        self.entity_maps = self.plugin.config.entity_maps if self.plugin.config.entity_maps else DynamicData()


    def _debug(self, message: str):
        _LOGGER.debug(f"Telegram plugin: CallbackInputBlock - {message}")


    def create_action_event_payloads(self, source_event: CallbackActionEvent) -> list[dict]:
        self._debug("Processing callback event from telegram")
        return [{
            ATTR_ENTITY: self.entity_maps.get(f"{source_event.payload.entity_source}", source_event.payload.entity_source),
            ATTR_TYPE: REACT_TYPE_NOTIFY,
            ATTR_ACTION: REACT_ACTION_FEEDBACK_RETRIEVED,
            ATTR_DATA: {
                ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK: source_event.payload.feedback,
                ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT: source_event.payload.acknowledgement,
                ATTR_EVENT_NOTIFY_PROVIDER: NOTIFY_PROVIDER_TELEGRAM,
                ATTR_EVENT_NOTIFY_PROVIDER_PAYLOAD: {
                    ATTR_EVENT_FEEDBACK_ITEM_CONVERSIONATION_ID: source_event.payload.chat_id,
                    ATTR_EVENT_FEEDBACK_ITEM_MESSAGE_ID: source_event.payload.message.message_id,
                    ATTR_EVENT_FEEDBACK_ITEM_TEXT: source_event.payload.message.text,
                }
            }
        }]


class CallbackActionEventPayloadMessage(DynamicData):
    def __init__(self, source: dict = None) -> None:
        super().__init__()

        self.message_id: str = None
        self.text: str = None

        self.load(source)

    
class CallbackActionEventPayload(DynamicData):
    type_hints: dict = { ATTR_MESSAGE: CallbackActionEventPayloadMessage }

    def __init__(self) -> None:
        super().__init__()
        
        self.feedback: str = None
        self.acknowledgement: str = None
        self.message: CallbackActionEventPayloadMessage = None
        
        self.entity_source: str = None
        self.args: list = None
        self.command: str = None
        self.user_id: str = None
        self.chat_id: str = None


    def load(self, source: dict) -> None:
        super().load(source)
        if self.user_id:
            self.entity_source = self.user_id
        if not self.entity_source and self.chat_id:
            self.entity_source = self.chat_id
        if not self.entity_source:
            self.entity_source = "unknown"
        if self.args:
            self.feedback = self.args[0] if len(self.args) > 0 else None
            self.acknowledgement = self.args[1] if len(self.args) > 1 else None

            
class CallbackActionEvent(ReactEvent[CallbackActionEventPayload]):

    def __init__(self, ha_event: HaEvent) -> None:
        super().__init__(ha_event,  CallbackActionEventPayload)
        

    @property
    def applies(self) -> bool:
        return self.payload.command == EVENTPAYLOAD_COMMAND_REACT
