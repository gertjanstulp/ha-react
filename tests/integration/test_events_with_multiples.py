import pytest

from homeassistant.core import HomeAssistant

from tests.common import FIXTURE_WORKFLOW_NAME
from tests.tst_context import TstContext

@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["multiple_actor"])
async def test_react_multiple_actor_1(hass: HomeAssistant, workflow_name, react_component):
    """
    Test for workflow with multiple actors using first actor:
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    await react_component.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["multiple_actor"])
async def test_react_multiple_actor_2(hass: HomeAssistant, workflow_name, react_component):
    """
    Test for workflow with multiple actors using second actor:
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    await react_component.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event(actor_index=1)
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record(actor_index=1)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["multiple_reactor"])
async def test_react_multiple_reactor(hass: HomeAssistant, workflow_name, react_component):
    """
    Test for workflow with multiple reactors:
    - No reaction entities should be created
    - An event should be sent for each reactor (2)
    - Event data should match configuration for each reactor (2)
    - Trace data should match configuration
    """

    await react_component.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received(expected_count=2)
        tc.verify_reaction_event_data(event_index=0, reactor_index=0)
        tc.verify_reaction_event_data(event_index=1, reactor_index=1)
        tc.verify_trace_record()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["multiple_entities"])
async def test_react_multiple_entities_1(hass: HomeAssistant, workflow_name, react_component):
    """
    Test for workflow with an actor containing multiple entities
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """
    
    await react_component.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["multiple_entities"])
async def test_react_multiple_entities_2(hass: HomeAssistant, workflow_name, react_component):
    """
    Test for workflow with an actor containing multiple entities
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """
    
    await react_component.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event(entity_index=1)
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record(actor_entity_index=1)
