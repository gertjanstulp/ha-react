from __future__ import annotations

from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from custom_components.react.base import ReactBase
from custom_components.react.const import (
    ATTR_ACTION, 
    ATTR_DATA, 
    ATTR_ENTITY,
    ATTR_NEW_STATE,
    ATTR_OLD_STATE,
    ATTR_TIMESTAMP, 
    ATTR_TYPE,
    REACT_ACTION_CHANGE, 
    REACT_TYPE_STATE,
    SIGNAL_ACTION_HANDLER_CREATED,
    SIGNAL_ACTION_HANDLER_DESTROYED, 
)
from custom_components.react.tasks.filters import ENTITY_ID_STATE_CHANGE_FILTER_STRATEGY, track_key
from custom_components.react.tasks.plugin.base import InputBlock
from custom_components.react.utils.events import ReactEvent, StateChangedEvent
from custom_components.react.utils.session import Session
from custom_components.react.utils.struct import ActorRuntime, StateConfig


class StateChangeInputBlock(InputBlock[StateConfig]):
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, StateChangedEvent)
        self.state_track_keys: list[str] = []


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


    def create_action_event_payloads(self, source_event: StateChangedEvent) -> list[dict]:
        source_event.session.debug(self.logger, f"State change caught: {source_event.payload.entity_id} ({source_event.payload.old_state.state if source_event.payload.old_state else None} -> {source_event.payload.new_state.state if source_event.payload.new_state else None})")
        return [{
            ATTR_ENTITY: source_event.payload.entity_id,
            ATTR_TYPE: REACT_TYPE_STATE,
            ATTR_ACTION: REACT_ACTION_CHANGE,
            ATTR_DATA: {
                ATTR_OLD_STATE: source_event.payload.old_state.state if source_event.payload.old_state else None,
                ATTR_NEW_STATE: source_event.payload.new_state.state if source_event.payload.new_state else None,
                ATTR_TIMESTAMP: 
                    source_event.payload.new_state.last_changed if source_event.payload.new_state else 
                    source_event.payload.old_state.last_changed if source_event.payload.old_state else 
                    None
            }
        }]


    @callback
    def async_track_actor(self, workflow_id: str, actor: ActorRuntime):
        self.update_tracker(True, actor)
                
    
    @callback
    def async_untrack_actor(self, workflow_id: str, actor: ActorRuntime):
        self.update_tracker(False, actor)


    def update_tracker(self, track: bool, actor: ActorRuntime):
        if REACT_TYPE_STATE in actor.type:
            for entity in actor.entity:
                state_track_key = track_key(self.__class__.__name__, entity)
                if track and state_track_key not in self.state_track_keys:
                    self.manager.track_state_change(ENTITY_ID_STATE_CHANGE_FILTER_STRATEGY.get_filter(entity, state_track_key), self)
                    self.state_track_keys.append(state_track_key)
                if not track and state_track_key in self.state_track_keys:
                    self.manager.untrack_key(self, state_track_key)
                    self.state_track_keys.remove(state_track_key)
