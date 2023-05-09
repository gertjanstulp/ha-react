from __future__ import annotations

from homeassistant.core import Event as HassEvent

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
from custom_components.react.tasks.plugin.base import PluginTransformTask
from custom_components.react.utils.events import Event
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData


_LOGGER = get_react_logger()


class CallbackTransformInTask(PluginTransformTask):
    def __init__(self, react: ReactBase, config: MobileAppConfig) -> None:
        super().__init__(react, EVENT_MOBILE_APP_CALLBACK, CallbackTransformEvent)
        self.entity_maps = config.entity_maps if config.entity_maps else DynamicData()


    def _debug(self, message: str):
        _LOGGER.debug(f"Mobile app plugin: CallbackTransformInTask - {message}")


    def create_action_event_payload(self, source_event: CallbackTransformEvent) -> dict:
        self._debug("Transforming callback event from mobile app")
        entity_id = self.entity_maps.get(source_event.payload.device_id, source_event.payload.device_id)
        return {
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
        }


class CallbackTransformEventPayload(DynamicData):
    def __init__(self, source: dict = None) -> None:
        super().__init__()

        self.action: str = None
        self.device_id: str = None
        self.tag: str = None
        self.message: str = None

        self.load(source)
        
            
class CallbackTransformEvent(Event[CallbackTransformEventPayload]):

    def __init__(self, hass_event: HassEvent) -> None:
        super().__init__(hass_event,  CallbackTransformEventPayload)
        

    @property
    def applies(self) -> bool:
        return (
            self.event_type == EVENT_MOBILE_APP_CALLBACK
        )
