from __future__ import annotations

from homeassistant.components.persistent_notification import DOMAIN as PERSISTENT_NOTIFICATION_DOMAIN
from homeassistant.core import Event as HaEvent

from custom_components.react.plugin.const import ATTR_OBJECT_ID
from custom_components.react.tasks.filters import DOMAIN_STATE_CHANGE_FILTER_STRATEGY
from custom_components.react.utils.events import StateChangedEvent
from custom_components.react.base import ReactBase
from custom_components.react.tasks.plugin.base import InputBlock
from custom_components.react.const import (
    ATTR_ACTION, 
    ATTR_DATA, 
    ATTR_ENTITY, 
    ATTR_TYPE,
    REACT_ACTION_DISMISSED, 
    REACT_TYPE_NOTIFY
)
from custom_components.react.utils.struct import DynamicData



class NotificationDismissedInputBlock(InputBlock[DynamicData]):
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, PersistentNotificationStateChangeEvent)
        self.track_state_change_filters = [DOMAIN_STATE_CHANGE_FILTER_STRATEGY.get_filter(PERSISTENT_NOTIFICATION_DOMAIN)]


    def create_action_event_payloads(self, source_event: PersistentNotificationStateChangeEvent) -> list[dict]:
        source_event.session.debug(self.logger, f"Persistent notification callback caught: '{source_event.payload.entity_id}' dismissed")
        return [{
            ATTR_ENTITY: PERSISTENT_NOTIFICATION_DOMAIN,
            ATTR_TYPE: REACT_TYPE_NOTIFY,
            ATTR_ACTION: REACT_ACTION_DISMISSED,
            ATTR_DATA: {
                ATTR_OBJECT_ID: source_event.payload.old_state.object_id
            }
        }]
    

class PersistentNotificationStateChangeEvent(StateChangedEvent):
    def __init__(self, ha_event: HaEvent) -> None:
        super().__init__(ha_event)


    @property
    def applies(self) -> bool:
        return (
            self.payload.old_state and
            self.payload.new_state == None
        )
