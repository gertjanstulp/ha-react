""""Store React data."""
from __future__ import annotations

from homeassistant.components.group import DOMAIN, GroupIntegrationRegistry
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.core import State
from homeassistant.const import (
    STATE_OFF, 
    STATE_ON, 
)

from custom_components.react.base import ReactBase
from custom_components.react.tasks.transform_base import BinaryStateData, StateChangedEvent, StateChangedEventPayload, StateData, StateTransformTask
from custom_components.react.const import (
    GROUP, 
    GROUP_PREFIX
)


async def async_setup_task(react: ReactBase) -> Task:
    """Set up this task."""
    return Task(react=react)


class BinaryGroupStateData(BinaryStateData):
    
    def __init__(self, event_payload: StateChangedEventPayload):
        super().__init__(GROUP_PREFIX, event_payload)


class Task(StateTransformTask):
    """ "React task base."""
    
    def __init__(self, react: ReactBase) -> None:
        super().__init__(react, GROUP_PREFIX, GROUP)
        self.can_run_disabled = True
        self.registry: GroupIntegrationRegistry = react.hass.data.get('group_registry')
        self.component: EntityComponent = react.hass.data.get(DOMAIN)
        self.state_cache: dict[str, dict] = {}


    def read_state_data(self, event: StateChangedEvent) -> StateData:
        states = self.get_states(event.payload)
        return BinaryStateData(GROUP_PREFIX, event.payload, states[STATE_ON], states[STATE_OFF])


    def get_states(self, payload: StateChangedEventPayload):
        test = self.state_cache.get(payload.entity_id, None)
        if not test:
            test = self.test_states([payload.new_state, payload.old_state], self.registry.on_off_mapping, STATE_ON, STATE_OFF)
            if not test:
                test = self.test_states([payload.new_state, payload.old_state], self.registry.off_on_mapping, STATE_OFF, STATE_ON)
            self.state_cache[payload.entity_id] = test
        return test


    def test_states(self, states: list[State], test_dict: dict[str, str], key1: str, key2: str):
        for state in states:
            if state and state.state in test_dict:
                return {
                    key1: state.state,
                    key2: test_dict[state.state]
                }
        return None