from __future__ import annotations
from typing import Type


from homeassistant.const import (
    ATTR_ENTITY_ID,
    EVENT_STATE_CHANGED,
    STATE_OFF,
    STATE_ON,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN
)
from homeassistant.core import Event as HassEvent, State, callback

from custom_components.react.base import ReactBase
from custom_components.react.tasks.base import ReactTask, ReactTaskType
from custom_components.react.const import (
    ACTION_AVAILABLE,
    ACTION_TOGGLE,
    ACTION_UNAVAILABLE,
    ATTR_ACTION,
    ATTR_ENTITY,
    ATTR_TYPE,
    EVENT_REACT_ACTION,
    SIGNAL_ACTION_HANDLER_CREATED,
    SIGNAL_ACTION_HANDLER_DESTROYED
)
from custom_components.react.utils.events import Event
from custom_components.react.utils.struct import ActorRuntime, DynamicData

from homeassistant.helpers.dispatcher import async_dispatcher_connect

class StateData:

    def __init__(self, entity_prefix: str, event_payload: StateChangedEventPayload):
        self.entity = event_payload.entity_id.replace(entity_prefix, '')
        self.actions = []
        
        self.old_state_value = event_payload.old_state.state if event_payload.old_state else None
        self.new_state_value = event_payload.new_state.state if event_payload.new_state else None

        if (self.old_state_value == STATE_UNAVAILABLE and self.new_state_value != STATE_UNAVAILABLE):
            self.actions.append(ACTION_AVAILABLE)
        if (self.old_state_value != STATE_UNAVAILABLE and self.old_state_value != STATE_UNKNOWN and self.new_state_value == STATE_UNAVAILABLE):
            self.actions.append(ACTION_UNAVAILABLE)
            

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

    def __init__(self, entity_prefix: str, event_payload: StateChangedEventPayload, on_state: str = STATE_ON, off_state: str = STATE_OFF):
        super().__init__(entity_prefix, event_payload)

        if (self.old_state_value == off_state and self.new_state_value == on_state):
            self.actions.append(on_state)
            self.actions.append(ACTION_TOGGLE)
        if (self.old_state_value == on_state and self.new_state_value == off_state):
            self.actions.append(off_state)
            self.actions.append(ACTION_TOGGLE)


class NonBinaryStateData(StateData):

    def __init__(self, entity_prefix: str, event_payload: StateChangedEventPayload):
        super().__init__(entity_prefix, event_payload)
        

class StateChangedEventPayload(DynamicData):
    def __init__(self, source: dict = None) -> None:
        super().__init__()

        self.entity_id: str = None
        self.old_state: State = None
        self.new_state: State = None

        self.load(source)


class StateChangedEvent(Event[StateChangedEventPayload]):

    def __init__(self, hass_event: HassEvent) -> None:
        super().__init__(hass_event,  StateChangedEventPayload)


    def applies(self) -> bool:
        return True

   
class StateTransformTask(ReactTask):
    
    def __init__(self, react: ReactBase, entity_prefix: str, type: str, payload_type: Type[StateChangedEventPayload] = StateChangedEventPayload) -> None:
        super().__init__(react)
        
        self.entity_prefix = entity_prefix
        self.type = type
        self.payload_type = payload_type

        self.entities = []
        self.events_with_filters = [(EVENT_STATE_CHANGED, self.async_filter)]
        async_dispatcher_connect(self.react.hass, SIGNAL_ACTION_HANDLER_CREATED, self.async_register_entity)
        async_dispatcher_connect(self.react.hass, SIGNAL_ACTION_HANDLER_DESTROYED, self.async_unregister_entity)


    @property
    def task_type(self) -> ReactTaskType:
        return ReactTaskType.RUNTIME

    
    @callback
    def async_filter(self, hass_event: HassEvent) -> bool:
        entity_id: str = hass_event.data.get(ATTR_ENTITY_ID, None)
        if entity_id and entity_id.startswith(self.entity_prefix):
            entity: str = entity_id.split('.')[1]
            return entity in self.entities
        return False
      

    async def async_execute(self, hass_event: HassEvent) -> None:
        """Execute the task."""
        event = StateChangedEvent(hass_event)
        state_data = self.read_state_data(event)
        react_events = state_data.to_react_events(self.type)
        for react_event in react_events:
            self.react.hass.bus.async_fire(EVENT_REACT_ACTION, react_event)

    
    def read_state_data(self, event: StateChangedEvent) -> StateData: 
        raise NotImplementedError()


    @callback
    def async_register_entity(self, workflow_id: str, actor: ActorRuntime):
        if self.type in actor.type:
            self.entities.extend(actor.entity)

    
    @callback
    def async_unregister_entity(self, workflow_id: str, actor: ActorRuntime):
        if actor.entity in self.entities:
            self.entities.remove(actor.entity)