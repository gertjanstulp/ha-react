from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Generic, TypeVar

from homeassistant.const import (
    STATE_OFF,
    STATE_ON,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN
)
from homeassistant.core import Event as HaEvent, callback, split_entity_id
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from custom_components.react.base import ReactBase
from custom_components.react.const import (
    ACTION_AVAILABLE,
    ACTION_CHANGE,
    ACTION_TOGGLE, 
    ACTION_UNAVAILABLE,
    ATTR_ACTION,
    ATTR_ENTITY,
    ATTR_TYPE,
    EVENT_REACT_ACTION, 
    SIGNAL_ACTION_HANDLER_CREATED, 
    SIGNAL_ACTION_HANDLER_DESTROYED,
)
from custom_components.react.tasks.base import ReactTask, ReactTaskType
from custom_components.react.tasks.filters import ENTITY_ID_STATE_CHANGE_FILTER_STRATEGY, track_key
from custom_components.react.utils.events import ReactEvent, StateChangedEvent, StateChangedEventPayload
from custom_components.react.utils.logger import format_data, get_react_logger
from custom_components.react.utils.struct import ActorRuntime, DynamicData

if TYPE_CHECKING:
    from custom_components.react.plugin.factory import Plugin

_LOGGER = get_react_logger()

T_config = TypeVar("T_config", bound=DynamicData)


class BlockBase(Generic[T_config], ReactTask):

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react)

        self.plugin: Plugin[T_config] = None


    def _build(self, plugin: Plugin[T_config]):
        self.plugin = plugin


    def load(self):
        pass


    def start(self):
        self.react.task_manager.register_task(self)


    @property
    def task_type(self) -> ReactTaskType:
        return ReactTaskType.BLOCK
    

class InputBlock():
    def create_action_event_payloads(self, *args) -> list[dict]:
        raise NotImplementedError()


    def produce_actions(self, react: ReactBase, time_key: str, *args):
        action_event_payloads = self.create_action_event_payloads(time_key, *args)
        for action_event_payload in action_event_payloads:
            _LOGGER.debug(f"InputBlock: sending action event: {format_data(**action_event_payload)}")
            react.hass.bus.async_fire(EVENT_REACT_ACTION, action_event_payload)


class EventBlock(Generic[T_config], BlockBase[T_config]):
    def __init__(self, react: ReactBase, e_type: type[ReactEvent]) -> None:
        super().__init__(react)
        
        self.e_type = e_type
        self.react_events: Dict[str, ReactEvent] = {}
        self.block_filter = self.async_filter
    
    
    @callback
    def async_filter(self, ha_event: HaEvent) -> bool:
        react_event = self.e_type(ha_event)
        if react_event.applies:
            self.set_action_event(ha_event, react_event)
            return True
        return False


    async def async_execute(self, ha_event: HaEvent) -> None:
        react_event = self.get_react_event(ha_event)
        await self.async_handle_event(react_event)
    

    async def async_handle_event(self, react_event: ReactEvent):
        raise NotImplementedError()


    def set_action_event(self, ha_event: HaEvent, react_event: ReactEvent):
        self.react_events[id(ha_event)] = react_event


    def get_react_event(self, ha_event: HaEvent) -> ReactEvent:
        return self.react_events.get(id(ha_event))


class EventInputBlock(Generic[T_config], EventBlock[T_config], InputBlock):
    def __init__(self, react: ReactBase, e_type: type[ReactEvent]):
        super().__init__(react, e_type)


    async def async_handle_event(self, react_event: ReactEvent):
        self.produce_actions(self.react, react_event)


class StateChangeInputBlock(Generic[T_config], EventInputBlock[T_config]):
    def __init__(self, react: ReactBase, type: str) -> None:
        super().__init__(react, StateChangedEvent)

        self.type = type

        async_dispatcher_connect(self.react.hass, SIGNAL_ACTION_HANDLER_CREATED, self.async_track_entity)
        async_dispatcher_connect(self.react.hass, SIGNAL_ACTION_HANDLER_DESTROYED, self.async_untrack_entity)


    def read_state_data(self, react_event: StateChangedEvent) -> StateChangeData: 
        raise NotImplementedError()
    
    
    def create_action_event_payloads(self, source_event: StateChangedEvent) -> list[dict]:
        state_data = self.read_state_data(source_event)
        react_events = state_data.to_react_events(self.type)
        return react_events


    @callback
    def async_track_entity(self, workflow_id: str, actor: ActorRuntime):
        if not self.type or self.type in actor.type:
            for entity in actor.entity:
                self.manager.track_state_change(
                    ENTITY_ID_STATE_CHANGE_FILTER_STRATEGY.get_filter(
                        f"{self.type}.{entity}",
                        track_key(workflow_id, actor.id, entity)
                    ),
                    self
                )
                

    
    @callback
    def async_untrack_entity(self, workflow_id: str, actor: ActorRuntime):
        if not self.type or self.type in actor.type:
            for entity in actor.entity:
                self.manager.untrack_entity(self, track_key(workflow_id, actor.id, entity))
    

class TimeInputBlock(Generic[T_config], BlockBase[T_config], InputBlock):

    async def async_execute(self, time_key: str, *args) -> None:
        self.produce_actions(self.react, time_key, *args)
    

class OutputBlock(Generic[T_config], EventBlock[T_config]):
    def __init__(self, react: ReactBase, e_type: type[ReactEvent]):
        super().__init__(react, e_type)




class StateChangeData:

    def __init__(self, event_payload: StateChangedEventPayload):
        self.entity = split_entity_id(event_payload.entity_id)[1]
        self.actions = []
        
        self.old_state_value = event_payload.old_state.state if event_payload.old_state else None
        self.new_state_value = event_payload.new_state.state if event_payload.new_state else None

        if (self.old_state_value == STATE_UNAVAILABLE and self.new_state_value != STATE_UNAVAILABLE):
            self.actions.append(ACTION_AVAILABLE)
        if (self.old_state_value != STATE_UNAVAILABLE and self.old_state_value != STATE_UNKNOWN and self.new_state_value == STATE_UNAVAILABLE):
            self.actions.append(ACTION_UNAVAILABLE)
        if self.old_state_value != self.new_state_value:        
            self.actions.append(ACTION_CHANGE)            


    def to_react_events(self, type: str):
        result = []
        for action in self.actions:
            result.append({
                ATTR_ENTITY: self.entity,
                ATTR_TYPE: type,
                ATTR_ACTION: action
            })
        return result


class BinaryStateChangeData(StateChangeData):

    def __init__(self, event_payload: StateChangedEventPayload, on_state: str = STATE_ON, off_state: str = STATE_OFF):
        super().__init__(event_payload)

        if (self.old_state_value == off_state and self.new_state_value == on_state):
            self.actions.append(on_state)
            self.actions.append(ACTION_TOGGLE)
        if (self.old_state_value == on_state and self.new_state_value == off_state):
            self.actions.append(off_state)
            self.actions.append(ACTION_TOGGLE)
        