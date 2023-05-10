from __future__ import annotations

from homeassistant.const import (
    ATTR_ENTITY_ID,
)
from homeassistant.core import Event as HaEvent, State

from custom_components.react.const import (
    ATTR_ACTION,
    ATTR_NEW_STATE,
    ATTR_OLD_STATE, 
    ATTR_TYPE,
)
from custom_components.react.exceptions import ReactException


class EventFilter():
    def __init__(self, filter_key: str, track_key: str = None) -> None:
        self.filter_key = filter_key
        self.track_key = track_key or filter_key


class EventFilterStrategy():

    def get_event_key(self, ha_event: HaEvent):
        raise NotImplementedError()
    

class TypeActionReactionFilterStrategy(EventFilterStrategy):
    def get_event_data(self, ha_event: HaEvent) -> tuple[str, str]:
        return ha_event.data.get(ATTR_TYPE, ""), ha_event.data.get(ATTR_ACTION, "")
    

    def _get_filter_key(self, type: str, action: str):
        return f"type={type}|action={action}"
    

    def get_event_key(self, ha_event: HaEvent):
        event_data = self.get_event_data(ha_event)
        return self._get_filter_key(*event_data)
    

    def get_filter(self, type: str, action: str, track_key: str = None) -> EventFilter:
        return EventFilter(self._get_filter_key(type, action), track_key)
    

TYPE_ACTION_REACTION_FILTER_STRATEGY = TypeActionReactionFilterStrategy()
ALL_REACTION_FILTER_STRATEGIES: list[EventFilterStrategy] = [
    TYPE_ACTION_REACTION_FILTER_STRATEGY,
]
    

class DomainStateChangeFilterStrategy(EventFilterStrategy):
    def _get_filter_key(self, domain: str):
        return f"domain={domain}"
    

    def get_event_key(self, ha_event: HaEvent):
        state: State = ha_event.data.get(ATTR_OLD_STATE, None)
        if not state:
            state = ha_event.data.get(ATTR_NEW_STATE, None)

        if not state:
            raise ReactException("Invalid event for event_key")

        return self._get_filter_key(state.domain)
    

    def get_filter(self, domain: str, track_key: str = None) -> EventFilter:
        return EventFilter(self._get_filter_key(domain), track_key)


class EntityIdStateChangeFilterStrategy(EventFilterStrategy):
    def _get_filter_key(self, entity_id: str):
        return f"entity_id={entity_id}"
    

    def get_event_key(self, ha_event: HaEvent):
        return self._get_filter_key(ha_event.data.get(ATTR_ENTITY_ID))
    

    def get_filter(self, entity_id, track_key: str = None) -> EventFilter:
        return EventFilter(self._get_filter_key(entity_id), track_key)
    

DOMAIN_STATE_CHANGE_FILTER_STRATEGY = DomainStateChangeFilterStrategy()
ENTITY_ID_STATE_CHANGE_FILTER_STRATEGY = EntityIdStateChangeFilterStrategy()
ALL_STATE_CHANGE_FILTER_STRATEGIES: list[EventFilterStrategy] = [
    DOMAIN_STATE_CHANGE_FILTER_STRATEGY,
    ENTITY_ID_STATE_CHANGE_FILTER_STRATEGY,
]


class EventTypeFilterStrategy(EventFilterStrategy):
    def _get_filter_key(self, event_type: str):
        return event_type
    

    def get_event_key(self, ha_event: HaEvent):
        return self._get_filter_key(ha_event.event_type)
    
        
    def get_filter(self, event_type, track_key: str = None) -> EventFilter:
        return EventFilter(self._get_filter_key(event_type), track_key)
        

EVENT_TYPE_FILTER_STRATEGY = EventTypeFilterStrategy()


def track_key(*args):
    return "|".join(args)