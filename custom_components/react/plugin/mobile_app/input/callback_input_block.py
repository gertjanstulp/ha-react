from __future__ import annotations

from homeassistant.core import Event as HaEvent

from custom_components.react.const import (
    ATTR_ACTION, 
    ATTR_DATA, 
    ATTR_ENTITY,
    ATTR_EVENT_FEEDBACK_ITEM_CONVERSIONATION_ID,
    ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK,
    ATTR_EVENT_FEEDBACK_ITEM_MESSAGE_ID,
    ATTR_EVENT_FEEDBACK_ITEM_TEXT,
    ATTR_EVENT_NOTIFY_PROVIDER,
    ATTR_EVENT_NOTIFY_PROVIDER_PAYLOAD, 
    ATTR_TYPE,
    REACT_ACTION_FEEDBACK_RETRIEVED,
    REACT_TYPE_NOTIFY
)
from custom_components.react.base import ReactBase
from custom_components.react.plugin.mobile_app.config import MobileAppConfig
from custom_components.react.plugin.mobile_app.const import (
    EVENT_MOBILE_APP_CALLBACK, 
    NOTIFY_PROVIDER_MOBILE_APP
)
from custom_components.react.tasks.filters import EVENT_TYPE_FILTER_STRATEGY
from custom_components.react.tasks.plugin.base import EventInputBlock
from custom_components.react.utils.events import ReactEvent
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData


_LOGGER = get_react_logger()


class CallbackInputBlock(EventInputBlock[MobileAppConfig]):
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, CallbackActionEvent)
        self.track_event_filters = [EVENT_TYPE_FILTER_STRATEGY.get_filter(EVENT_MOBILE_APP_CALLBACK)]


    def load(self):
        self.entity_maps = self.plugin.config.entity_maps if self.plugin.config.entity_maps else DynamicData()


    def _debug(self, message: str):
        _LOGGER.debug(f"Mobile app plugin: CallbackInputBlock - {message}")


    def create_action_event_payloads(self, source_event: CallbackActionEvent) -> list[dict]:
        self._debug("Processing callback event from mobile app")
        entity_id = self.entity_maps.get(source_event.payload.device_id, source_event.payload.device_id)
        return [{
            ATTR_ENTITY: entity_id,
            ATTR_TYPE: REACT_TYPE_NOTIFY,
            ATTR_ACTION: REACT_ACTION_FEEDBACK_RETRIEVED,
            ATTR_DATA: {
                ATTR_EVENT_FEEDBACK_ITEM_FEEDBACK: source_event.payload.action,
                ATTR_EVENT_NOTIFY_PROVIDER: NOTIFY_PROVIDER_MOBILE_APP,
                ATTR_EVENT_NOTIFY_PROVIDER_PAYLOAD: {
                    ATTR_EVENT_FEEDBACK_ITEM_CONVERSIONATION_ID: source_event.payload.tag,
                    ATTR_EVENT_FEEDBACK_ITEM_MESSAGE_ID: entity_id,
                    ATTR_EVENT_FEEDBACK_ITEM_TEXT: source_event.payload.message,
                }
            }
        }]


class CallbackActionEventPayload(DynamicData):
    def __init__(self, source: dict = None) -> None:
        super().__init__()

        self.action: str = None
        self.device_id: str = None
        self.tag: str = None
        self.message: str = None

        self.load(source)
        
            
class CallbackActionEvent(ReactEvent[CallbackActionEventPayload]):

    def __init__(self, ha_event: HaEvent) -> None:
        super().__init__(ha_event, CallbackActionEventPayload)
