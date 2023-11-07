from __future__ import annotations

from homeassistant.const import (
    ATTR_DOMAIN,
    ATTR_ENTITY_ID,
    EVENT_STATE_CHANGED,
)
from homeassistant.core import Event as HaEvent, State

from custom_components.react.const import (
    ATTR_ACTION,
    ATTR_NEW_STATE,
    ATTR_OLD_STATE,
    ATTR_STATE, 
    ATTR_TYPE,
    EVENT_REACT_REACTION,
)
from custom_components.react.exceptions import ReactException


class EventFilter():
    def __init__(self, event_type: str, filter_key: str, track_key: str = None, match_data: dict = None, *args) -> None:
        self.event_type = event_type
        self.filter_key = filter_key
        self.track_key = track_key or filter_key
        self.match_data = match_data
        self.args = args


    def applies(self, ha_event: HaEvent) -> bool:
        result = True
        if self.match_data:
            result = ha_event.data | self.match_data == ha_event.data
        return result


class EventFilterStrategy():

    def get_event_key(self, ha_event: HaEvent):
        raise NotImplementedError()


########## Reaction filters ##########


class ReactionEventFilterStrategy(EventFilterStrategy):
    def get_reaction_filter(self, filter_key: str, track_key: str = None, *args):
        return EventFilter(EVENT_REACT_REACTION, filter_key, track_key=track_key, *args)
    

class TypeActionReactionEventFilterStrategy(ReactionEventFilterStrategy):
    def _get_filter_key(self, type: str, action: str):
        return f"type={type}|action={action}"
    

    def get_event_data(self, ha_event: HaEvent) -> tuple[str, str]:
        return ha_event.data.get(ATTR_TYPE, ""), ha_event.data.get(ATTR_ACTION, "")
    

    def get_event_key(self, ha_event: HaEvent):
        event_data = self.get_event_data(ha_event)
        return self._get_filter_key(*event_data)
    
    
    def get_filter(self, type: str, action: str, track_key: str = None, *args) -> EventFilter:
        return self.get_reaction_filter(self._get_filter_key(type, action), track_key, *args)
    

TYPE_ACTION_REACTION_FILTER_STRATEGY = TypeActionReactionEventFilterStrategy()
ALL_REACTION_FILTER_STRATEGIES: list[ReactionEventFilterStrategy] = [
    TYPE_ACTION_REACTION_FILTER_STRATEGY,
]


########## State change filters ##########

class StateChangeFilter(EventFilter):
    def __init__(self, 
        event_type: str, 
        filter_key: str, 
        track_key: str = None, 
        old_state: str = None, 
        new_state: str = None, 
        match_data: dict = None, 
        *args
    ) -> None:
        super().__init__(event_type, filter_key, track_key, match_data, *args)
        self.old_state = old_state
        self.new_state = new_state


    def applies(self, ha_event: HaEvent) -> bool:
        result = True
        if (self.old_state or self.new_state):
            old_state_value = ""
            if old_state := ha_event.data.get(ATTR_OLD_STATE):
                old_state_value = old_state.get(ATTR_STATE, None) if isinstance(old_state, dict) else old_state.state
            new_state_value = ""
            if new_state := ha_event.data.get(ATTR_NEW_STATE):
                new_state_value = new_state.get(ATTR_STATE, None) if isinstance(new_state, dict) else new_state.state
            result = old_state_value == self.old_state and new_state_value == self.new_state
        return result


class StateChangeFilterStrategy(EventFilterStrategy):
    def get_state_change_filter(self, filter_key: str, track_key: str = None, old_state: str = None, new_state: str = None, *args):
        return StateChangeFilter(EVENT_STATE_CHANGED, filter_key, track_key=track_key, old_state=old_state, new_state=new_state, *args)
    

class DomainStateChangeFilterStrategy(StateChangeFilterStrategy):
    def _get_filter_key(self, domain: str):
        return f"domain={domain}"
    

    def get_event_key(self, ha_event: HaEvent):
        state: State = ha_event.data.get(ATTR_OLD_STATE, None)
        if not state:
            state = ha_event.data.get(ATTR_NEW_STATE, None)

        if not state:
            raise ReactException("Invalid event for event_key")

        if isinstance(state, dict):
            return self._get_filter_key(state.get(ATTR_DOMAIN))
        else:
            return self._get_filter_key(state.domain)
    

    def get_filter(self, domain: str, track_key: str = None, *args) -> EventFilter:
        return self.get_state_change_filter(self._get_filter_key(domain), track_key=track_key, *args)


class EntityIdStateChangeFilterStrategy(StateChangeFilterStrategy):
    def _get_filter_key(self, entity_id: str):
        return f"entity_id={entity_id}"
    

    def get_event_key(self, ha_event: HaEvent):
        return self._get_filter_key(ha_event.data.get(ATTR_ENTITY_ID))
    

    def get_filter(self, entity_id, track_key: str = None, old_state: str = None, new_state: str = None, *args) -> EventFilter:
        return self.get_state_change_filter(self._get_filter_key(entity_id), track_key=track_key, old_state=old_state, new_state=new_state, *args)


DOMAIN_STATE_CHANGE_FILTER_STRATEGY = DomainStateChangeFilterStrategy()
ENTITY_ID_STATE_CHANGE_FILTER_STRATEGY = EntityIdStateChangeFilterStrategy()
ALL_STATE_CHANGE_FILTER_STRATEGIES: list[StateChangeFilterStrategy] = [
    DOMAIN_STATE_CHANGE_FILTER_STRATEGY,
    ENTITY_ID_STATE_CHANGE_FILTER_STRATEGY,
]


########## Eventtype filters ##########


class EventTypeFilterStrategy(EventFilterStrategy):
    def _get_filter_key(self, event_type: str):
        return f"event_type={event_type}|has_data=false"
    

    def get_event_key(self, ha_event: HaEvent):
        return self._get_filter_key(ha_event.event_type)
    
        
    def get_filter(self, event_type: str, track_key: str = None) -> EventFilter:
        return EventFilter(event_type, self._get_filter_key(event_type), track_key)


class EventTypeAndDataFilterStrategy(EventFilterStrategy):
    def _get_filter_key(self, event_type) -> str:
        return f"event_type={event_type}|has_data=true"


    def get_event_key(self, ha_event: HaEvent) -> str:
        return self._get_filter_key(ha_event.event_type)
    

    def get_filter(self, event_type: str, match_data: dict[str, str], track_key: str = None):
        return EventFilter(
            event_type=event_type, 
            filter_key=self._get_filter_key(event_type), 
            track_key=track_key, 
            match_data=match_data
        )
        

EVENT_TYPE_FILTER_STRATEGY = EventTypeFilterStrategy()
EVENT_TYPE_AND_DATA_FILTER_STRATEGY = EventTypeAndDataFilterStrategy()
ALL_EVENTTYPE_FILTER_STRATEGIES: list[EventFilterStrategy] = [
    EVENT_TYPE_FILTER_STRATEGY,
    EVENT_TYPE_AND_DATA_FILTER_STRATEGY,
]


def track_key(*args):
    return "|".join(args)