from typing import Any
from homeassistant.core import Event, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.const import (
    ATTR_ENTITY_ID,
    EVENT_STATE_CHANGED, 
    STATE_OFF, 
    STATE_ON,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)

from .base import ReactTask
from ..base import ReactBase
from ..lib.config import MultiItem

from ..const import (
    ACTION_AVAILABLE,
    ACTION_TOGGLE,
    ACTION_UNAVAILABLE,
    ATTR_ACTION,
    ATTR_ENTITY, 
    ATTR_TYPE,
    EVENT_REACT_ACTION,
    NEW_STATE,
    OLD_STATE,
    SIGNAL_ACTION_HANDLER_CREATED,
    SIGNAL_ACTION_HANDLER_DESTROYED,
)


class StateData:

    def __init__(self, entity_prefix: str, event_data: dict[str, Any]):
        self.entity = event_data.get(ATTR_ENTITY_ID, '').replace(entity_prefix, '')
        self.actions = []
        
        self.old_state_value: Any = None
        self.new_state_value: Any = None


    def to_react_events(self, type: str):
        result = []
        for action in self.actions:
            result.append({
                ATTR_ENTITY: self.entity,
                ATTR_TYPE: type,
                ATTR_ACTION: action
            })
        return result


class BinaryStateData(StateData):

    def __init__(self, entity_prefix: str, event_data: dict[str, Any]):
        super().__init__(entity_prefix, event_data)
        old_state = event_data.get(OLD_STATE, None)
        new_state = event_data.get(NEW_STATE, None)
        self.old_state_value = old_state.state if old_state else None
        self.new_state_value = new_state.state if new_state else None

        if (self.old_state_value == STATE_UNAVAILABLE and self.new_state_value != STATE_UNAVAILABLE):
            self.actions.append(ACTION_AVAILABLE)
        if (self.old_state_value != STATE_UNAVAILABLE and self.old_state_value != STATE_UNKNOWN and self.new_state_value == STATE_UNAVAILABLE):
            self.actions.append(ACTION_UNAVAILABLE)
        if (self.old_state_value == STATE_OFF and self.new_state_value == STATE_ON):
            self.actions.append(STATE_ON)
            self.actions.append(ACTION_TOGGLE)
        if (self.old_state_value == STATE_ON and self.new_state_value == STATE_OFF):
            self.actions.append(STATE_OFF)
            self.actions.append(ACTION_TOGGLE)


class NonBinaryStateData(StateData):

    def __init__(self, entity_prefix: str, event_data: dict[str, Any]):
        super().__init__(entity_prefix, event_data)
        
        old_state = event_data.get(OLD_STATE, None)
        new_state = event_data.get(NEW_STATE, None)
        self.old_state_value = old_state.state if old_state else None
        self.new_state_value = new_state.state if new_state else None

        if (self.old_state_value == STATE_UNAVAILABLE and self.new_state_value != STATE_UNAVAILABLE):
            self.actions.append(ACTION_AVAILABLE)
        if (self.old_state_value != STATE_UNAVAILABLE and self.old_state_value != STATE_UNKNOWN and self.new_state_value == STATE_UNAVAILABLE):
            self.actions.append(ACTION_UNAVAILABLE)

   
class StateTransformTask(ReactTask):
    
    def __init__(self, react: ReactBase, prefix: str, type: str) -> None:
        super().__init__(react)
        
        self.prefix = prefix
        self.type = type
        self.entities = []
        self.events_with_filters = [(EVENT_STATE_CHANGED, self.async_filter)]
        async_dispatcher_connect(self.react.hass, SIGNAL_ACTION_HANDLER_CREATED, self.async_register_entity)
        async_dispatcher_connect(self.react.hass, SIGNAL_ACTION_HANDLER_DESTROYED, self.async_unregister_entity)
        

    
    @callback
    def async_filter(self, event: Event) -> bool:
        if ATTR_ENTITY_ID in event.data and event.data[ATTR_ENTITY_ID].startswith(self.prefix):
            entity: str = event.data.get(ATTR_ENTITY_ID).split('.')[1]
            return entity in self.entities
        return False
      

    async def async_execute(self, event: Event) -> None:
        """Execute the task."""
        state_data = self.read_state_data( event)
        react_events = state_data.to_react_events(self.type)
        for react_event in react_events:
            self.react.hass.bus.async_fire(EVENT_REACT_ACTION, react_event)

    
    def read_state_data(self, event: Event) -> StateData: 
        raise NotImplementedError()


    @callback
    def async_register_entity(self, entity: MultiItem, type: MultiItem):
        if self.type in type:
            self.entities.extend(entity)

    
    @callback
    def async_unregister_entity(self, entity: MultiItem):
        if entity in self.entities:
            self.entities.remove(entity)
