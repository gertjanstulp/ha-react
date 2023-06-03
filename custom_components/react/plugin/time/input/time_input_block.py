from __future__ import annotations

from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from custom_components.react.base import ReactBase

from custom_components.react.const import (
    ACTOR_ENTITY_TIME, 
    ACTOR_TYPE_CLOCK, 
    ACTOR_TYPE_PATTERN, 
    ATTR_ACTION, 
    ATTR_ENTITY, 
    ATTR_TYPE, 
    SIGNAL_ACTION_HANDLER_CREATED, 
    SIGNAL_ACTION_HANDLER_DESTROYED,
)
from custom_components.react.tasks.filters import track_key
from custom_components.react.tasks.plugin.base import TimeInputBlock as TimeInputBlockBase
from custom_components.react.utils.struct import ActorRuntime, DynamicData
from custom_components.react.utils.time import parse_time_data


class TimeInputBlock(TimeInputBlockBase[DynamicData]):
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react)

        self.action_track_keys: list[str] = []


    def load(self):
        async_dispatcher_connect(self.react.hass, SIGNAL_ACTION_HANDLER_CREATED, self.async_track_actor)
        async_dispatcher_connect(self.react.hass, SIGNAL_ACTION_HANDLER_DESTROYED, self.async_untrack_actor)


    def create_action_event_payloads(self, time_key: str, type: str = None) -> list[dict]:
        return [{
            ATTR_ENTITY: ACTOR_ENTITY_TIME,
            ATTR_TYPE: type,
            ATTR_ACTION: time_key
        }]


    @callback
    def async_track_actor(self, workflow_id: str, actor: ActorRuntime):
        self.update_tracker(True, actor)

    
    @callback
    def async_untrack_actor(self, workflow_id: str, actor: ActorRuntime):
        self.update_tracker(False, actor)


    def update_tracker(self, track: bool, actor: ActorRuntime):
        if ACTOR_ENTITY_TIME in actor.entity and (ACTOR_TYPE_CLOCK in actor.type or ACTOR_TYPE_PATTERN in actor.type):
            for action in actor.action:
                action_track_key = track_key(self.__class__.__name__, action)
                if track and action_track_key not in self.action_track_keys:
                    self.manager.track_time(parse_time_data(action), action, action_track_key, self, actor.type.first)
                    self.action_track_keys.append(action_track_key)
                if not track and action_track_key in self.action_track_keys:
                    self.manager.untrack_time(self, action_track_key)
                    self.action_track_keys.remove(action_track_key)