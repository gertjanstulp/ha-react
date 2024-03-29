from __future__ import annotations

from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.util import dt as dt_util

from custom_components.react.base import ReactBase
from custom_components.react.const import (
    ACTOR_ENTITY_CLOCK,
    ACTOR_ENTITY_PATTERN,
    ACTOR_TYPE_TIME,
    ATTR_ACTION, 
    ATTR_ENTITY, 
    ATTR_TYPE, 
    SIGNAL_ACTION_HANDLER_CREATED, 
    SIGNAL_ACTION_HANDLER_DESTROYED,
)
from custom_components.react.tasks.filters import track_key
from custom_components.react.tasks.plugin.base import InputBlock
from custom_components.react.utils.events import TimeEvent
from custom_components.react.utils.struct import ActorRuntime, DynamicData
from custom_components.react.utils.time import parse_time_data


class TimeInputBlock(InputBlock[DynamicData]):
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, TimeEvent)
        self.action_track_keys: list[str] = []


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


    def create_action_event_payloads(self, source_event: TimeEvent) -> list[dict]:
        source_event.session.debug(self.logger, f"Time change caught: {source_event.payload.entity} value {source_event.payload.time_key} matched current time ({dt_util.now(time_zone=dt_util.DEFAULT_TIME_ZONE).strftime('%H:%M:%S')})")
        return [{
            ATTR_ENTITY: source_event.payload.entity,
            ATTR_TYPE: ACTOR_TYPE_TIME,
            ATTR_ACTION: source_event.payload.time_key,
        }]


    @callback
    def async_track_actor(self, workflow_id: str, actor: ActorRuntime):
        self.update_tracker(True, actor)

    
    @callback
    def async_untrack_actor(self, workflow_id: str, actor: ActorRuntime):
        self.update_tracker(False, actor)


    def update_tracker(self, track: bool, actor: ActorRuntime):
        if ACTOR_TYPE_TIME in actor.type and (ACTOR_ENTITY_CLOCK in actor.entity or ACTOR_ENTITY_PATTERN in actor.entity):
            for action in actor.action:
                action_track_key = track_key(self.__class__.__name__, action)
                if track and action_track_key not in self.action_track_keys:
                    self.manager.track_time(parse_time_data(action), action, action_track_key, self, actor.entity.first)
                    self.action_track_keys.append(action_track_key)
                if not track and action_track_key in self.action_track_keys:
                    self.manager.untrack_key(self, action_track_key)
                    self.action_track_keys.remove(action_track_key)