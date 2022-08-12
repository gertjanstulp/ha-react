import pytest

from homeassistant.core import HomeAssistant

from tests.tst_context import TstContext
from tests.common import FIXTURE_TEST_NAME

@pytest.mark.parametrize(FIXTURE_TEST_NAME, ["binary_sensor_available"])
async def test_react_binary_sensor_available(hass: HomeAssistant, test_name, react_component, input_boolean_component, template_component):
    """
    Test for workflow for binary_sensor availability:
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """
    
    await react_component.async_setup(test_name)

    tc = TstContext(hass, test_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_entity_not_found()
        await input_boolean_component.async_turn_off("test_binary_sensor_available")
        await input_boolean_component.async_turn_on("test_binary_sensor_available")
        await hass.async_block_till_done()
        tc.verify_reaction_entity_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()

@pytest.mark.parametrize(FIXTURE_TEST_NAME, ["binary_sensor_unavailable"])
async def test_react_binary_sensor_unavailable(hass: HomeAssistant, test_name, react_component, input_boolean_component, template_component):
    """
    Test for workflow for binary_sensor unavailability:
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """
    
    await react_component.async_setup(test_name)

    tc = TstContext(hass, test_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_entity_not_found()
        await input_boolean_component.async_turn_on("test_binary_sensor_available")
        await input_boolean_component.async_turn_off("test_binary_sensor_available")
        await hass.async_block_till_done()
        tc.verify_reaction_entity_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()