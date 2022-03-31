from typing import Any
from homeassistant.const import ATTR_ENTITY_ID, EVENT_HOMEASSISTANT_STARTED, EVENT_STATE_CHANGED, STATE_OFF, STATE_ON
from homeassistant.core import CoreState, Event, HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_call_later

from .. import const as co

class StateData:
    def __init__(self, entity: str):
        self.entity = entity

    def to_react_events(self, type: str):
        raise NotImplementedError()
        
class BinaryStateData:
    def __init__(self, entity: str, state_event_data: dict[str, Any]):
        self.entity = entity
        old_state = state_event_data.get(co.OLD_STATE, '')
        new_state = state_event_data.get(co.NEW_STATE)
        old_state_value = old_state.state if old_state else None
        new_state_value = new_state.state if new_state else None
        self.actions = []

        if (old_state_value == STATE_OFF and new_state_value == STATE_ON):
            self.actions.append(STATE_ON)
            self.actions.append(co.ACTION_TOGGLE)
        if (old_state_value == STATE_ON and new_state_value == STATE_OFF):
            self.actions.append(STATE_OFF)
            self.actions.append(co.ACTION_TOGGLE)

    def to_react_events(self, type: str):
        result = []
        for action in self.actions:
            result.append({
                co.ATTR_ENTITY: self.entity,
                co.ATTR_TYPE: type,
                co.ATTR_ACTION: action
            })
        return result

class BinarySensorStateData(BinaryStateData):
    def __init__(self, state_event_data: dict[str, Any]):
        entity = state_event_data.get(ATTR_ENTITY_ID, '').replace(co.BINARY_SENSOR_PREFIX, '')
        super().__init__(entity, state_event_data)


class GroupStateData(BinaryStateData):
    def __init__(self, state_event_data: dict[str, Any]):
        entity = state_event_data.get(ATTR_ENTITY_ID, '').replace(co.GROUP_PREFIX, '')
        super().__init__(entity, state_event_data)


class SwitchStateData(BinaryStateData):
    def __init__(self, state_event_data: dict[str, Any]):
        entity = state_event_data.get(ATTR_ENTITY_ID, '').replace(co.SWITCH_PREFIX, '')
        super().__init__(entity, state_event_data)


class StateTransformer:
    def __init__(self, hass: HomeAssistant, prefix: str, type: str):
        self.hass = hass
        self.prefix = prefix
        self.type = type
        self.state = co.STATE_INIT

        @callback
        def handle_startup(_event):
            @callback
            def async_timer_finished(_now):
                self.state = co.STATE_READY
                async_dispatcher_send(self.hass, co.EVENT_STARTED)

            async_call_later(hass, 5, async_timer_finished)

        if hass.state == CoreState.running:
            handle_startup(None)
        else:
            hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, handle_startup)


    def start(self):
        self.cancel_event_listen = self.hass.bus.async_listen(EVENT_STATE_CHANGED, self.state_changed, self.event_pre_filter)
        if self.state != co.STATE_INIT:
            self.state = co.STATE_READY


    def stop(self):
        self.state = co.STATE_STOPPED
        if self.cancel_event_listen:
            self.cancel_event_listen()


    @callback
    def event_pre_filter(self, event: Event):
        return co.ATTR_ENTITY_ID in event.data and event.data[co.ATTR_ENTITY_ID].startswith(self.prefix)


    async def state_changed(self, event: Event):
        if not self.state == co.STATE_READY: return
        state_data = self.read_state_data(event)
        react_events = state_data.to_react_events(self.type)
        for react_event in react_events:
            self.hass.bus.async_fire(co.EVENT_REACT_ACTION, react_event)


    def read_state_data(self, event: Event) -> StateData: 
        raise NotImplementedError()


class BinaryStateTransformer(StateTransformer):
    def __init__(self, hass: HomeAssistant, prefix: str, type: str):
        super().__init__(hass, prefix, type)
    

class BinarySensorTransformer(BinaryStateTransformer):
    def __init__(self, hass: HomeAssistant):
        super().__init__(hass, co.BINARY_SENSOR_PREFIX, co.BINARY_SENSOR)


    def read_state_data(self, event: Event) -> StateData:
        return BinarySensorStateData(event.data)


class GroupTransformer(BinaryStateTransformer):
    def __init__(self, hass: BinaryStateTransformer):
        super().__init__(hass, co.GROUP_PREFIX, co.GROUP)


    def read_state_data(self, event: Event) -> StateData:
        return GroupStateData(event.data)


class SwitchTransformer(BinaryStateTransformer):
    def __init__(self, hass: BinaryStateTransformer):
        super().__init__(hass, co.SWITCH_PREFIX, co.SWITCH)


    def read_state_data(self, event: Event) -> StateData:
        return SwitchStateData(event.data)


class TransformerManager:
    def __init__(self, hass: HomeAssistant) -> None:
        self.binary_state_transformer = BinarySensorTransformer(hass)
        self.group_transformer = GroupTransformer(hass)
        self.switch_transformer = SwitchTransformer(hass)


    def start(self):
        self.binary_state_transformer.start()
        self.group_transformer.start()
        self.switch_transformer.start()


    def stop(self):
        self.binary_state_transformer.stop()
        self.group_transformer.stop()
        self.switch_transformer.stop()
