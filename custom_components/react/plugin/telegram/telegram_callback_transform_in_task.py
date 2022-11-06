from __future__ import annotations

from homeassistant.components.telegram_bot import ATTR_CHAT_ID, ATTR_MESSAGE, ATTR_MESSAGEID, EVENT_TELEGRAM_CALLBACK, ATTR_TEXT
from homeassistant.core import Event as HassEvent

from custom_components.react.const import ATTR_ACTION, ATTR_DATA, ATTR_ENTITY, ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT, ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK, ATTR_EVENT_PLUGIN, ATTR_TYPE, EVENTPAYLOAD_COMMAND_REACT, ATTR_EVENT_PLUGIN_PAYLOAD, REACT_ACTION_FEEDBACK, REACT_ACTION_FEEDBACK_RETRIEVED, REACT_TYPE_NOTIFY
from custom_components.react.utils.events import Event
from custom_components.react.base import ReactBase
from custom_components.react.tasks.defaults.default_task import DefaultTransformTask
from custom_components.react.utils.struct import DynamicData

from custom_components.react.plugin.telegram.const import PLUGIN_NAME


class TelegramCallbackTransformInTask(DefaultTransformTask):
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, EVENT_TELEGRAM_CALLBACK, TelegramCallbackTransformEvent)


    def create_action_event_payload(self, source_event: TelegramCallbackTransformEvent) -> dict:
        entity_maps = self.react.configuration.workflow_config.entity_maps_config
        return {
            ATTR_ENTITY: entity_maps.get(source_event.payload.entity_source, None),
            ATTR_TYPE: REACT_TYPE_NOTIFY,
            ATTR_ACTION: REACT_ACTION_FEEDBACK_RETRIEVED,
            ATTR_DATA: {
                ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK: source_event.payload.feedback,
                ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT: source_event.payload.acknowledgement,
                ATTR_EVENT_PLUGIN: PLUGIN_NAME,
                ATTR_EVENT_PLUGIN_PAYLOAD: {
                    ATTR_TEXT: source_event.payload.message.text,
                    ATTR_CHAT_ID: source_event.payload.chat_id,
                    ATTR_MESSAGEID: source_event.payload.message.message_id
                }
            }
        }


class TelegramNotifyFeedbackEventPayloadMessage(DynamicData):
    def __init__(self, source: dict = None) -> None:
        super().__init__()

        self.message_id: str = None
        self.text: str = None

        self.load(source)

    
class TelegramCallbackTransformEventPayload(DynamicData):
    type_hints: dict = { ATTR_MESSAGE: TelegramNotifyFeedbackEventPayloadMessage }

    def __init__(self) -> None:
        super().__init__()
        
        self.feedback: str = None
        self.acknowledgement: str = None
        self.message: TelegramNotifyFeedbackEventPayloadMessage = None
        
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

            
class TelegramCallbackTransformEvent(Event[TelegramCallbackTransformEventPayload]):

    def __init__(self, hass_event: HassEvent) -> None:
        super().__init__(hass_event, TelegramCallbackTransformEventPayload)
        

    @property
    def applies(self) -> bool:
        return (
            self.event_type == EVENT_TELEGRAM_CALLBACK and
            self.payload.command == EVENTPAYLOAD_COMMAND_REACT
        )