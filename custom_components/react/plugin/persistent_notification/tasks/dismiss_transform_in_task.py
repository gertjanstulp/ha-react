from __future__ import annotations

from homeassistant.const import (
    EVENT_STATE_CHANGED
)
from homeassistant.core import Event as HassEvent
from homeassistant.components.persistent_notification import (
    DOMAIN as PERSISTENT_NOTIFICATION_DOMAIN, 
)
from custom_components.react.plugin.persistent_notification.const import (
    ATTR_NEW_STATE,
    ATTR_OBJECT_ID,
    ATTR_OLD_STATE
)

from custom_components.react.utils.events import Event
from custom_components.react.base import ReactBase
from custom_components.react.tasks.plugin.base import PluginTransformTask
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import DynamicData
from custom_components.react.const import (
    ATTR_ACTION, 
    ATTR_DATA, 
    ATTR_ENTITY, 
    ATTR_TYPE,
    REACT_ACTION_DISMISSED, 
    REACT_TYPE_NOTIFY
)


_LOGGER = get_react_logger()


class DismissTransformInTask(PluginTransformTask):
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, EVENT_STATE_CHANGED, DismissTransformEvent)


    def _debug(self, message: str):
        _LOGGER.debug(f"Persistent notification plugin: DismissTransformInTask - {message}")


    def create_action_event_payload(self, source_event: DismissTransformEvent) -> dict:
        self._debug("Transforming dismiss event from persistent_notification")
        return {
            ATTR_ENTITY: PERSISTENT_NOTIFICATION_DOMAIN,
            ATTR_TYPE: REACT_TYPE_NOTIFY,
            ATTR_ACTION: REACT_ACTION_DISMISSED,
            ATTR_DATA: {
                ATTR_OBJECT_ID: source_event.payload.old_state.object_id
            }
        }


class DismissTransformEventPayloadState(DynamicData):
    def __init__(self, source: dict = None) -> None:
        super().__init__()

        self.domain: str = None
        self.object_id: str = None

        self.load(source)

    
class DismissTransformEventPayload(DynamicData):
    type_hints: dict = { 
        ATTR_OLD_STATE: DismissTransformEventPayloadState,
        ATTR_NEW_STATE: DismissTransformEventPayloadState 
    }

    def __init__(self) -> None:
        super().__init__()
        
        self.entity_id: str = None
        self.old_state: DismissTransformEventPayloadState = None
        self.new_state: DismissTransformEventPayloadState = None
        
            
class DismissTransformEvent(Event[DismissTransformEventPayload]):

    def __init__(self, hass_event: HassEvent) -> None:
        super().__init__(hass_event,  DismissTransformEventPayload)
        

    @property
    def applies(self) -> bool:
        return (
            self.event_type == EVENT_STATE_CHANGED and
            self.payload.old_state and
            self.payload.old_state.domain == PERSISTENT_NOTIFICATION_DOMAIN and 
            self.payload.new_state == None
        )
