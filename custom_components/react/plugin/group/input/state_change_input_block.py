from homeassistant.components.group import (
    DOMAIN, 
    REG_KEY as GROUP_REG_KEY, 
    GroupIntegrationRegistry,
)
from homeassistant.const import (
    STATE_OFF, 
    STATE_ON, 
)
from homeassistant.core import State
from homeassistant.helpers.entity_component import EntityComponent

from custom_components.react.base import ReactBase
from custom_components.react.tasks.plugin.base import BinaryStateChangeData, StateChangeInputBlock, StateChangeData
from custom_components.react.utils.events import StateChangedEvent, StateChangedEventPayload
from custom_components.react.utils.struct import DynamicData

class GroupStateChangeInputBlock(StateChangeInputBlock[DynamicData]):
    """ "React task base."""
    
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, DOMAIN)
        self.registry: GroupIntegrationRegistry = react.hass.data.get(GROUP_REG_KEY)
        self.component: EntityComponent = react.hass.data.get(DOMAIN)
        self.state_cache: dict[str, dict] = {}


    def read_state_data(self, react_event: StateChangedEvent) -> StateChangeData:
        states = self.get_states(react_event.payload)
        if states:
            return BinaryStateChangeData(react_event.payload, states[STATE_ON], states[STATE_OFF])
        else:
            return None


    def get_states(self, payload: StateChangedEventPayload):
        states = self.state_cache.get(payload.entity_id, None)
        if not states:
            states = self.test_states([payload.new_state, payload.old_state], self.registry.on_off_mapping, STATE_ON, STATE_OFF)
            if not states:
                states = self.test_states([payload.new_state, payload.old_state], self.registry.off_on_mapping, STATE_OFF, STATE_ON)
            if states:
                self.state_cache[payload.entity_id] = states
        
        return states


    def test_states(self, states: list[State], test_dict: dict[str, str], key1: str, key2: str):
        for state in states:
            if state and state.state in test_dict:
                return {
                    key1: state.state,
                    key2: test_dict[state.state]
                }
        return None