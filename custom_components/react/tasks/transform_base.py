from typing import Any
from homeassistant.core import Event, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.const import (
    ATTR_ENTITY_ID,
    EVENT_STATE_CHANGED, 
    STATE_OFF, 
    STATE_ON,
)

from .base import ReactTask
from ..base import ReactBase

from ..const import (
    ACTION_CHANGE,
    ACTION_TOGGLE,
    ALARM_PREFIX,
    ATTR_ACTION,
    ATTR_ENTITY, 
    ATTR_TYPE,
    BINARY_SENSOR_PREFIX,
    DEVICE_TRACKER_PREFIX,
    EVENT_REACT_ACTION,
    GROUP_PREFIX,
    LIGHT_PREFIX,
    MEDIAPLAYER_PREFIX,
    NEW_STATE,
    OLD_STATE,
    PERSON_PREFIX,
    SENSOR_PREFIX,
    SIGNAL_PROPERTY_COMPLETE,
    SWITCH_PREFIX,
)


class StateData:
    def __init__(self, entity_prefix: str, event_data: dict[str, Any]):
        self.entity = event_data.get(ATTR_ENTITY_ID, '').replace(entity_prefix, '')
        self.actions = []

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
        old_state_value = old_state.state if old_state else None
        new_state_value = new_state.state if new_state else None

        if (old_state_value == STATE_OFF and new_state_value == STATE_ON):
            self.actions.append(STATE_ON)
            self.actions.append(ACTION_TOGGLE)
        if (old_state_value == STATE_ON and new_state_value == STATE_OFF):
            self.actions.append(STATE_OFF)
            self.actions.append(ACTION_TOGGLE)


class NonBinaryStateData(StateData):
    def __init__(self, entity_prefix: str, event_data: dict[str, Any]):
        super().__init__(entity_prefix, event_data)
        
        old_state = event_data.get(OLD_STATE, None)
        new_state = event_data.get(NEW_STATE, None)
        self.old_state_value = old_state.state if old_state else None
        self.new_state_value = new_state.state if new_state else None


class SensorStateData(NonBinaryStateData):
    def __init__(self, event_data: dict[str, Any]):
        super().__init__(SENSOR_PREFIX, event_data)

        if self.new_state_value != self.old_state_value:
            self.actions.append(ACTION_CHANGE)


class BinarySensorStateData(BinaryStateData):
    def __init__(self, event_data: dict[str, Any]):
        super().__init__(BINARY_SENSOR_PREFIX, event_data)


class PersonStateData(NonBinaryStateData):
    def __init__(self, event_data: dict[str, Any]):
        super().__init__(PERSON_PREFIX, event_data)

        if self.old_state_value != self.new_state_value:
            self.actions.append(self.new_state_value)
        

class DeviceTrackerStateData(NonBinaryStateData):
    def __init__(self, event_data: dict[str, Any]):
        super().__init__(DEVICE_TRACKER_PREFIX, event_data)

        if self.old_state_value != self.new_state_value:
            self.actions.append(self.new_state_value)


class MediaPlayerStateData(NonBinaryStateData):
    def __init__(self, event_data: dict[str, Any]):
        super().__init__(MEDIAPLAYER_PREFIX, event_data)

        if self.old_state_value != self.new_state_value:
            self.actions.append(self.new_state_value)


class GroupStateData(BinaryStateData):
    def __init__(self, event_data: dict[str, Any]):
        super().__init__(GROUP_PREFIX, event_data)


class SwitchStateData(BinaryStateData):
    def __init__(self, event_data: dict[str, Any]):
        super().__init__(SWITCH_PREFIX, event_data)


class LightStateData(BinaryStateData):
    def __init__(self, event_data: dict[str, Any]):
        super().__init__(LIGHT_PREFIX, event_data)


class AlarmStateData(NonBinaryStateData):
    def __init__(self, event_data: dict[str, Any]):
        super().__init__(ALARM_PREFIX, event_data)

        if self.old_state_value != self.new_state_value:
            self.actions.append(self.new_state_value)


class StateTransformTask(ReactTask):
    def __init__(self, react: ReactBase, prefix: str, type: str) -> None:
        super().__init__(react)
        self.prefix = prefix
        self.type = type
        self.entities = []
        self.events_with_filters = [(EVENT_STATE_CHANGED, self.async_filter)]
        async_dispatcher_connect(self.react.hass, SIGNAL_PROPERTY_COMPLETE, self.async_register_entity)

    
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
    def async_register_entity(self, entity: str, type: str):
        if type == self.type:
            self.entities.append(entity)
