from __future__ import annotations

from homeassistant.components.telegram_bot import ATTR_CHAT_ID, ATTR_MESSAGEID, EVENT_TELEGRAM_CALLBACK, ATTR_TEXT
from homeassistant.core import Event
from homeassistant.components.telegram_bot import ATTR_MESSAGE

from custom_components.react.const import ATTR_ACTION, ATTR_DATA, ATTR_ENTITY, ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT, ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK, ATTR_EVENT_PLUGIN, ATTR_TYPE, EVENTDATA_COMMAND_REACT, ATTR_EVENT_PLUGIN_PAYLOAD, REACT_ACTION_FEEDBACK, REACT_ACTION_FEEDBACK_RETRIEVED, REACT_TYPE_NOTIFY
from custom_components.react.plugin.telegram.const import PLUGIN_NAME
from custom_components.react.utils.events import ReactEvent
from custom_components.react.base import ReactBase
from custom_components.react.tasks.defaults.default_task import DefaultTransformInTask
from custom_components.react.utils.struct import DynamicData


class TelegramCallbackTransformInTask(DefaultTransformInTask):
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, EVENT_TELEGRAM_CALLBACK, TelegramCallbackTransformEvent)


    def create_action_event_data(self, source_event: TelegramCallbackTransformEvent) -> dict:
        entity_maps = self.react.configuration.workflow_config.entity_maps_config
        return {
            ATTR_ENTITY: entity_maps.get(source_event.data.entity_source, None),
            ATTR_TYPE: REACT_TYPE_NOTIFY,
            ATTR_ACTION: REACT_ACTION_FEEDBACK_RETRIEVED,
            ATTR_DATA: {
                ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK: source_event.data.feedback,
                ATTR_EVENT_FEEDBACK_ITEM_ACKNOWLEDGEMENT: source_event.data.acknowledgement,
                ATTR_EVENT_PLUGIN: PLUGIN_NAME,
                ATTR_EVENT_PLUGIN_PAYLOAD: {
                    ATTR_TEXT: source_event.data.message.text,
                    ATTR_CHAT_ID: source_event.data.chat_id,
                    ATTR_MESSAGEID: source_event.data.message.message_id
                }
            }
        }


class TelegramNotifyFeedbackEventDataMessage(DynamicData):
    def __init__(self, source: dict = None) -> None:
        super().__init__()

        self.message_id: str = None
        self.text: str = None

        self.load(source)

    
class TelegramCallbackTransformEventData(DynamicData):
    type_hints: dict = { ATTR_MESSAGE: TelegramNotifyFeedbackEventDataMessage }

    def __init__(self) -> None:
        super().__init__()
        
        self.feedback: str = None
        self.acknowledgement: str = None
        self.message: TelegramNotifyFeedbackEventDataMessage = None
        
        self.entity_source: str = None
        self.args: list = None
        self.command: str = None
        self.user_id: str = None
        self.chat_id: str = None


    def load(self, source: dict) -> None:
        super().load(source)
        if self.args:
            self.feedback = self.args[0] if len(self.args) > 0 else None
            self.acknowledgement = self.args[1] if len(self.args) > 1 else None

            
class TelegramCallbackTransformEvent(ReactEvent[TelegramCallbackTransformEventData]):

    def __init__(self, event: Event) -> None:
        super().__init__(event, TelegramCallbackTransformEventData)
        
        self.event_type = event.event_type
        if self.data.user_id:
            self.data.entity_source = self.data.user_id
        if not self.data.entity_source and self.data.chat_id:
            self.data.entity_source = self.data.chat_id
        if not self.data.entity_source:
            self.data.entity_source = "unknown"
        

    @property
    def applies(self) -> bool:
        return (
            self.event_type == EVENT_TELEGRAM_CALLBACK and
            self.data.command == EVENTDATA_COMMAND_REACT
        )