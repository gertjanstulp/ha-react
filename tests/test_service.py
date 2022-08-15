import pytest

from homeassistant.core import HomeAssistant

from tests.tst_context import TstContext
from tests.common import FIXTURE_WORKFLOW_NAME

@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["immediate"])
async def test_react_call_trigger_service(hass: HomeAssistant, workflow_name, react_component):
    """
    Test for workflow for binary_sensor availability:
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """
    
    await react_component.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_entity_not_found()
        await react_component.async_call_trigger_service("react.workflow_immediate")
        await hass.async_block_till_done()
        tc.verify_reaction_entity_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()