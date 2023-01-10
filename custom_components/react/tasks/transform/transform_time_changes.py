from __future__ import annotations

import re

from datetime import datetime, time

from homeassistant.core import CALLBACK_TYPE, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.event import async_track_time_change

from custom_components.react.base import ReactBase
from custom_components.react.const import ACTOR_ENTITY_TIME, ACTOR_TYPE_CLOCK, ACTOR_TYPE_PATTERN, ATTR_ACTION, ATTR_ENTITY, ATTR_TYPE, EVENT_REACT_ACTION, SIGNAL_ACTION_HANDLER_CREATED, SIGNAL_ACTION_HANDLER_DESTROYED
from custom_components.react.tasks.base import ReactTask
from custom_components.react.utils.struct import ActorRuntime, MultiItem


async def async_setup_task(react: ReactBase) -> Task:
    """Set up this task."""
    return Task(react=react)


class Task(ReactTask):
    """ "React task base."""

    def __init__(self, react: ReactBase) -> None:
        super().__init__(react)

        self.can_run_disabled = True
        self.cancelers: dict[str] = {}
        async_dispatcher_connect(self.react.hass, SIGNAL_ACTION_HANDLER_CREATED, self.async_register_entity)
        async_dispatcher_connect(self.react.hass, SIGNAL_ACTION_HANDLER_DESTROYED, self.async_unregister_entity)


    @callback
    def async_register_entity(self, workflow_id: str, actor: ActorRuntime):
        if ACTOR_ENTITY_TIME in actor.entity and (ACTOR_TYPE_CLOCK in actor.type or ACTOR_TYPE_PATTERN in actor.type):
            for act in actor.action:
                time_data,time_key,event_key = self.create_event_keys(workflow_id, actor.id, act)
                async def async_time_change(time: datetime):
                    react_event = {
                        ATTR_ENTITY: ACTOR_ENTITY_TIME,
                        ATTR_TYPE: actor.type.first,
                        ATTR_ACTION: time_key
                    }
                    self.react.hass.bus.async_fire(EVENT_REACT_ACTION, react_event)
                cancel = async_track_time_change(
                    self.react.hass,
                    async_time_change,
                    time_data.hour,
                    time_data.minute,
                    time_data.second)
                self.cancelers[event_key] = cancel

    
    @callback
    def async_unregister_entity(self, workflow_id: str, actor: ActorRuntime):
        if ACTOR_ENTITY_TIME in actor.entity and (ACTOR_TYPE_CLOCK in actor.type or ACTOR_TYPE_PATTERN in actor.type):
            for act in actor.action:
                _, _, event_key = self.create_event_keys(workflow_id, actor.id, act)
                canceler = self.cancelers.pop(event_key, None)
                if canceler:
                    canceler()
    

    def create_event_keys(self, workflow_id: str, actor_id: str, action: str) -> tuple[TimeData, str, str]:
        clockformat = "%H:%M:%S"
        clockvalue: datetime = None
        try:
            clockvalue = datetime.strptime(action, clockformat)
            time_key = clockvalue.strftime("%H:%M:%S")
            time_data = TimeData(clockvalue.hour, clockvalue.minute, clockvalue.second)
        except ValueError:
            # Do not catch exception here, should be propagated to caller
            value,type = parse_pattern(action)
            time_key = f"{value}{type}"
            time_data = TimeData(
                f"/{value}" if type == "h" else None,
                f"/{value}" if type == "m" else None,
                f"/{value}" if type == "s" else None,
            )
        
        event_key = f"{workflow_id}_{actor_id}_{time_key}"

        return (time_data, time_key, event_key)


def parse_pattern(value: str) -> tuple[int, str]:
    hour_pattern = "^(2[0-3]|[01]?[0-9])(h)$"
    minute_pattern = "^([0-5]?[0-9])(m)$"
    second_pattern = "^([0-5]?[0-9])(s)$"
    result = -1
    type: str = None

    match = re.match(hour_pattern, value)
    if not match:
        match = re.match(minute_pattern, value)
        if not match:
            match = re.match(second_pattern, value)

    if not match:
        raise ValueError()

    return (int(match.group(1)), match.group(2))


class TimeData():
    def __init__(self, hour: str = None, minute: str = None, second: str = None) -> None:
        self.hour = hour
        self.minute = minute
        self.second = second
