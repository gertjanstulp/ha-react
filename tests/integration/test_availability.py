from asyncio import sleep
import pytest

from homeassistant.core import HomeAssistant

from tests.tst_context import TstContext
from tests.common import FIXTURE_WORKFLOW_NAME

@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["binary_sensor_available_test"])
async def test_binary_sensor_available(hass: HomeAssistant, workflow_name, react_component, virtual_component, binary_sensor_component):
    """
    Test for workflow for binary_sensor availability:
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """
    
    vc = await virtual_component
    await binary_sensor_component
    react_comp = await react_component
    await react_comp.async_setup(workflow_name)


    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await vc.async_set_available("binary_sensor", "binary_sensor_available_test")
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["binary_sensor_unavailable_test"])
async def test_binary_sensor_unavailable(hass: HomeAssistant, workflow_name, react_component, virtual_component, binary_sensor_component):
    """
    Test for workflow for binary_sensor unavailability:
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """
    
    vc = await virtual_component
    await binary_sensor_component
    comp = await react_component
    await comp.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await vc.async_set_unavailable("binary_sensor", "binary_sensor_unavailable_test")
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()