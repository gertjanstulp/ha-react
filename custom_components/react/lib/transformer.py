from typing import Any

from .domain_data import DomainData
from homeassistant.const import ATTR_ENTITY_ID, EVENT_HOMEASSISTANT_STARTED, EVENT_STATE_CHANGED, STATE_OFF, STATE_ON
from homeassistant.core import CoreState, Event, HomeAssistant, callback
from homeassistant.helpers.event import async_call_later

from .. import const as co
from .dispatcher import get as Dispatcher

class StateData:
    def __init__(self, entity: str):
        self.entity = entity
        self.actions = []

    def to_react_events(self, type: str):
        result = []
        for action in self.actions:
            result.append({
                co.ATTR_ENTITY: self.entity,
                co.ATTR_TYPE: type,
                co.ATTR_ACTION: action
            })
        return result


class BinaryStateData(StateData):
    def __init__(self, entity: str, state_event_data: dict[str, Any]):
        super().__init__(entity)
        old_state = state_event_data.get(co.OLD_STATE, '')
        new_state = state_event_data.get(co.NEW_STATE)
        old_state_value = old_state.state if old_state else None
        new_state_value = new_state.state if new_state else None

        if (old_state_value == STATE_OFF and new_state_value == STATE_ON):
            self.actions.append(STATE_ON)
            self.actions.append(co.ACTION_TOGGLE)
        if (old_state_value == STATE_ON and new_state_value == STATE_OFF):
            self.actions.append(STATE_OFF)
            self.actions.append(co.ACTION_TOGGLE)


class SensorStateData(StateData):
    def __init__(self, state_event_data: dict[str, Any]):
        entity = state_event_data.get(ATTR_ENTITY_ID, '').replace(co.SENSOR_PREFIX, '')
        super().__init__(entity)

        old_state = state_event_data.get(co.OLD_STATE, '')
        new_state = state_event_data.get(co.NEW_STATE)
        old_state_value = old_state.state if old_state else None
        new_state_value = new_state.state if new_state else None

        if new_state_value != old_state_value:
            self.actions.append(co.ACTION_CHANGE)
        

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
        self.entities = []

        @callback
        def handle_startup(_event):
            @callback
            def async_timer_finished(_now):
                self.state = co.STATE_READY

            async_call_later(hass, co.HA_STARTUP_DELAY, async_timer_finished)

        if hass.state == CoreState.running:
            handle_startup(None)
        else:
            hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, handle_startup)


    def register_entity(self, entity: str):
        if not entity in self.entities:
            self.entities.append(entity)


    def start(self):
        Dispatcher(self.hass).connect_event(EVENT_STATE_CHANGED, self.async_state_changed, self.async_event_pre_filter)
        if self.state != co.STATE_INIT:
            self.state = co.STATE_READY


    def stop(self):
        self.state = co.STATE_STOPPED
        # if self.cancel_event_listen:
        #     self.cancel_event_listen()


    @callback
    def async_event_pre_filter(self, event: Event) -> bool:
        if self.state != co.STATE_READY: return False
        if co.ATTR_ENTITY_ID in event.data and event.data[co.ATTR_ENTITY_ID].startswith(self.prefix):
            entity: str = event.data.get(co.ATTR_ENTITY_ID).split('.')[1]
            return entity in self.entities


    @callback
    def async_state_changed(self, event: Event):
        if not self.state == co.STATE_READY: return
        state_data = self.read_state_data(event)
        react_events = state_data.to_react_events(self.type)
        for react_event in react_events:
            Dispatcher(self.hass).send_event(co.EVENT_REACT_ACTION, react_event)


    def read_state_data(self, event: Event) -> StateData: 
        raise NotImplementedError()


class SensorTransformer(StateTransformer):
    def __init__(self, hass: HomeAssistant):
        super().__init__(hass, co.SENSOR_PREFIX, co.SENSOR)


    def read_state_data(self, event: Event) -> StateData:
        return SensorStateData(event.data)


class BinarySensorTransformer(StateTransformer):
    def __init__(self, hass: HomeAssistant):
        super().__init__(hass, co.BINARY_SENSOR_PREFIX, co.BINARY_SENSOR)


    def read_state_data(self, event: Event) -> StateData:
        return BinarySensorStateData(event.data)


class GroupTransformer(StateTransformer):
    def __init__(self, hass: HomeAssistant):
        super().__init__(hass, co.GROUP_PREFIX, co.GROUP)


    def read_state_data(self, event: Event) -> StateData:
        return GroupStateData(event.data)


class SwitchTransformer(StateTransformer):
    def __init__(self, hass: HomeAssistant):
        super().__init__(hass, co.SWITCH_PREFIX, co.SWITCH)


    def read_state_data(self, event: Event) -> StateData:
        return SwitchStateData(event.data)


class TransformerManager:
    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self.transformers: dict[str, StateTransformer] = {
            co.BINARY_SENSOR: BinarySensorTransformer(hass),
            co.GROUP: GroupTransformer(hass),
            co.SWITCH: SwitchTransformer(hass),
            co.SENSOR: SensorTransformer(hass),
        }


    def start(self):
        Dispatcher(self.hass).connect_signal(co.SIGNAL_PROPERTY_COMPLETE, self.async_register_entity)
        for transformer in self.transformers.values():
            transformer.start()


    def stop(self):
        for transformer in self.transformers.values():
            transformer.stop()


    @callback
    def async_register_entity(self, entity: str, type: str):
        if type in self.transformers.keys():
            self.transformers.get(type).register_entity(entity)


def get(hass: HomeAssistant) -> TransformerManager:
    if co.DOMAIN_BOOTSTRAPPER in hass.data:
        return hass.data[co.DOMAIN_BOOTSTRAPPER].transformer_manager
    return None
