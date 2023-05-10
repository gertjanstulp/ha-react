from __future__ import annotations

import itertools

from homeassistant.const import EVENT_STATE_CHANGED
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
from custom_components.react.tasks.filters import ENTITY_ID_STATE_CHANGE_FILTER_STRATEGY, EVENT_TYPE_FILTER_STRATEGY, track_key
from custom_components.react.tasks.plugin.base import EventInputBlock
from custom_components.react.utils.events import StateChangedEvent
from custom_components.react.utils.logger import get_react_logger
from custom_components.react.utils.struct import ActorRuntime, StateConfig

_LOGGER = get_react_logger()


class StateChangeInputBlock(EventInputBlock[StateConfig]):
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, StateChangedEvent)

        async_dispatcher_connect(self.react.hass, SIGNAL_ACTION_HANDLER_CREATED, self.async_track_entity)
        async_dispatcher_connect(self.react.hass, SIGNAL_ACTION_HANDLER_DESTROYED, self.async_untrack_entity)
        

    def _debug(self, message: str):
        _LOGGER.debug(f"State plugin: StateChangeInputBlock - {message}")


    def create_action_event_payloads(self, source_event: StateChangedEvent) -> list[dict]:
        self._debug("Processing state change event")
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
    def async_track_entity(self, workflow_id: str, actor: ActorRuntime):
        if REACT_TYPE_STATE in actor.type:
            for entity in actor.entity:
                self.manager.track_state_change(
                    ENTITY_ID_STATE_CHANGE_FILTER_STRATEGY.get_filter(
                        entity,
                        track_key(workflow_id, actor.id, entity)
                    ),
                    self
                )
                

    
    @callback
    def async_untrack_entity(self, workflow_id: str, actor: ActorRuntime):
        if REACT_TYPE_STATE in actor.type:
            for entity in actor.entity:
                self.manager.untrack_entity(self, track_key(workflow_id, actor.id, entity))