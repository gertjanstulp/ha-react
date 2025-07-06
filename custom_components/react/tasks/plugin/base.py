from __future__ import annotations
from logging import Logger

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
    ATTR_ID,
    ATTR_SESSION_ID,
    ATTR_ENTITY,
    ATTR_TYPE,
    EVENT_REACT_ACTION, 
    SIGNAL_ACTION_HANDLER_CREATED, 
    SIGNAL_ACTION_HANDLER_DESTROYED,
)
from custom_components.react.tasks.base import ReactTask, ReactTaskType
from custom_components.react.tasks.filters import ENTITY_ID_STATE_CHANGE_FILTER_STRATEGY, track_key
from custom_components.react.utils.events import ReactEvent, StateChangedEvent, StateChangedEventPayload
from custom_components.react.utils.logger import format_data
from custom_components.react.utils.session import Session
from custom_components.react.utils.struct import ActorRuntime, DynamicData

if TYPE_CHECKING:
    from custom_components.react.plugin.factory import Plugin

T_config = TypeVar("T_config", bound=DynamicData)


class BlockBase(Generic[T_config], ReactTask):

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, skip_task_log=True)

        self.plugin: Plugin[T_config] = None


    def _build(self, plugin: Plugin[T_config]):
        self.plugin = plugin


    @property
    def logger(self) -> Logger:
        return self.plugin.logger if self.plugin else None


    def load(self):
        self.react.task_manager.register_task(self)


    def on_start(self):
        self.plugin.logger.debug(f"Starting {self.__class__.__name__}")


    def on_unload(self):
        self.plugin.logger.debug(f"Unloading {self.__class__.__name__}")


    @property
    def task_type(self) -> ReactTaskType:
        return ReactTaskType.BLOCK
    

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
        self.react.session_manager.load_session(react_event)
        await self.async_handle_event(react_event)
    

    async def async_handle_event(self, react_event: ReactEvent):
        raise NotImplementedError()


    def set_action_event(self, ha_event: HaEvent, react_event: ReactEvent):
        self.react_events[id(ha_event)] = react_event


    def get_react_event(self, ha_event: HaEvent) -> ReactEvent:
        return self.react_events.get(id(ha_event))


class InputBlock(Generic[T_config], EventBlock[T_config]):
    def __init__(self, react: ReactBase, e_type: type[ReactEvent]):
        super().__init__(react, e_type)


    async def async_handle_event(self, react_event: ReactEvent):
        action_event_payloads = self.create_action_event_payloads(react_event)
        session_payload = {ATTR_SESSION_ID: react_event.session.id}
        for action_event_payload in action_event_payloads:
            react_event.session.debug(self.logger, f"Sending action event: {format_data(**action_event_payload)}")
            self.react.hass.bus.async_fire(EVENT_REACT_ACTION, action_event_payload | session_payload)


    def create_action_event_payloads(self, source_event: ReactEvent) -> list[dict]:
        raise NotImplementedError()


class StateChangeInputBlock(Generic[T_config], InputBlock[T_config]):
    def __init__(self, react: ReactBase, type: str) -> None:
        super().__init__(react, StateChangedEvent)

        self.type = type
        self.entity_track_keys: list[str] = []


    def load(self):
        super().load()
        self.manager.wrap_unloader(
            async_dispatcher_connect(self.react.hass, SIGNAL_ACTION_HANDLER_CREATED, self.async_track_actor),
            self.id,
            SIGNAL_ACTION_HANDLER_CREATED,
        )
        self.manager.wrap_unloader(
            async_dispatcher_connect(self.react.hass, SIGNAL_ACTION_HANDLER_DESTROYED, self.async_untrack_actor),
            self.id,
            SIGNAL_ACTION_HANDLER_DESTROYED,
        )


    def read_state_data(self, react_event: StateChangedEvent) -> StateChangeData: 
        raise NotImplementedError()
    
    
    def create_action_event_payloads(self, source_event: StateChangedEvent) -> list[dict]:
        react_events: list[dict] = []
        state_data = self.read_state_data(source_event)
        if state_data:
            react_events = state_data.to_react_events(self.type)
            if react_events:
                source_event.session.debug(self.logger, f"State change caught: {source_event.payload.entity_id} ({source_event.payload.old_state.state if source_event.payload.old_state else None} -> {source_event.payload.new_state.state if source_event.payload.new_state else None})")
        return react_events


    @callback
    def async_track_actor(self, workflow_id: str, actor: ActorRuntime):
        self.update_tracker(True, actor)

    
    @callback
    def async_untrack_actor(self, workflow_id: str, actor: ActorRuntime):
        self.update_tracker(False, actor)


    def update_tracker(self, track: bool, actor: ActorRuntime):
        if not self.type or self.type in actor.type:
            for entity in actor.entity:
                entity_track_key = track_key(self.__class__.__name__, self.type, entity)
                if track and entity_track_key not in self.entity_track_keys:
                    self.manager.track_state_change(ENTITY_ID_STATE_CHANGE_FILTER_STRATEGY.get_filter(f"{self.type}.{entity}",track_key=entity_track_key), self)
                    self.entity_track_keys.append(entity_track_key)
                if not track and entity_track_key in self.entity_track_keys:
                    self.manager.untrack_key(self, entity_track_key)
                    self.entity_track_keys.remove(entity_track_key)


class OutputBlock(Generic[T_config], EventBlock[T_config]):
    def __init__(self, react: ReactBase, e_type: type[ReactEvent]):
        super().__init__(react, e_type)
    

class StateChangeData:

    def __init__(self, event_payload: StateChangedEventPayload):
        self.entity = split_entity_id(event_payload.entity_id)[1]
        self.actions = []
        
        self.old_state_value = event_payload.old_state.state if event_payload.old_state else None
        self.new_state_value = event_payload.new_state.state if event_payload.new_state else None
        self.old_state_attributes = event_payload.old_state.attributes if event_payload.old_state else None
        self.new_state_attributes = event_payload.new_state.attributes if event_payload.new_state else None

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
                ATTR_ACTION: action,
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
        