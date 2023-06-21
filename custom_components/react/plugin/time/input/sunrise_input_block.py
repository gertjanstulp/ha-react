from __future__ import annotations
from datetime import timedelta

from homeassistant.const import SUN_EVENT_SUNRISE
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.util import dt as dt_util
from homeassistant.helpers.config_validation import time_period_str

from custom_components.react.base import ReactBase
from custom_components.react.const import (
    ACTOR_ENTITY_SUN,
    ACTOR_TYPE_TIME,
    ATTR_ACTION,
    ATTR_DATA, 
    ATTR_ENTITY, 
    ATTR_TYPE, 
    SIGNAL_ACTION_HANDLER_CREATED, 
    SIGNAL_ACTION_HANDLER_DESTROYED,
)
from custom_components.react.plugin.time.const import ATTR_OFFSET, DEFAULT_OFFSET
from custom_components.react.tasks.filters import track_key
from custom_components.react.tasks.plugin.base import InputBlock
from custom_components.react.utils.events import TimeEvent
from custom_components.react.utils.struct import ActorRuntime, DynamicData


class SunriseInputBlock(InputBlock[DynamicData]):
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, TimeEvent)
        self._action_track_keys: list[str] = []


    def load(self):
        super().load()

        @callback
        def track(workflow_id: str, actor: ActorRuntime):
            self._update_tracker(True, actor)

        @callback
        def untrack(workflow_id: str, actor: ActorRuntime):
            self._update_tracker(False, actor)

        self.manager.wrap_unloader(
            async_dispatcher_connect(self.react.hass, SIGNAL_ACTION_HANDLER_CREATED, track),
            self.id,
            SIGNAL_ACTION_HANDLER_CREATED,
        )
        self.manager.wrap_unloader(
            async_dispatcher_connect(self.react.hass, SIGNAL_ACTION_HANDLER_DESTROYED, untrack),
            self.id,
            SIGNAL_ACTION_HANDLER_DESTROYED,
        )


    def create_action_event_payloads(self, source_event: TimeEvent) -> list[dict]:
        source_event.session.debug(self.logger, f"Sunrise caught: {source_event.payload.entity} value {source_event.payload.time_key} matched sunrise time ({dt_util.now(time_zone=dt_util.DEFAULT_TIME_ZONE).strftime('%H:%M:%S')})")
        return [{
            ATTR_ENTITY: SUN_EVENT_SUNRISE,
            ATTR_TYPE: ACTOR_TYPE_TIME,
            ATTR_ACTION: source_event.payload.time_key.split("|")[-1],
        }]
    

    def _update_tracker(self, track: bool, actor: ActorRuntime):
        if SUN_EVENT_SUNRISE in actor.entity and ACTOR_TYPE_TIME in actor.type:
            for action in actor.action:
                action_track_key = track_key(self.__class__.__name__, action)
                if track and action_track_key not in self._action_track_keys:
                    offset: timedelta = time_period_str(action) if action and action != DEFAULT_OFFSET else None
                    self.manager.track_sun(SUN_EVENT_SUNRISE, action_track_key, self, offset, action)
                    self._action_track_keys.append(action_track_key)
                if not track and action_track_key in self._action_track_keys:
                    self.manager.untrack_key(self, action_track_key)
                    self._action_track_keys.remove(action_track_key)