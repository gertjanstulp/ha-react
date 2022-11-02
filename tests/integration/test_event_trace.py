import pytest
from homeassistant.core import HomeAssistant

from tests.common import FIXTURE_WORKFLOW_NAME
from tests.tst_context import TstContext

@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["trace"])
async def test_react_trace_switched_off_actor_1(hass: HomeAssistant, workflow_name, react_component, input_boolean_component):
    """
    Test for workflow with complex trace structure where actor 1 is triggered and the test_trace is turned off:
    - No reaction entity should be created
    - One event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    await react_component.async_setup(workflow_name)
    await input_boolean_component.async_turn_off("test_trace")
    
    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_react_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data(reactor_index=1)
        tc.verify_trace_record(
            expected_reactor_condition_results=[False, True]
        )


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["trace"])
async def test_react_trace_switched_on_actor_1(hass: HomeAssistant, workflow_name, react_component, input_boolean_component):
    """
    Test for workflow with complex trace structure where actor 1 is triggered and the test_trace is turned on:
    - No reaction entity should be created
    - No events should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    await react_component.async_setup(workflow_name)
    await input_boolean_component.async_turn_on("test_trace")

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_react_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_not_received()
        tc.verify_trace_record(
            expected_actor_condition_result=False
        )


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["trace"])
async def test_react_trace_switched_off_actor_2(hass: HomeAssistant, workflow_name, react_component, input_boolean_component):
    """
    Test for workflow with complex trace structure where actor 1 is triggered and the test_trace is turned off:
    - No reaction entity should be created
    - One event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    await react_component.async_setup(workflow_name)
    await input_boolean_component.async_turn_off("test_trace")
    
    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_react_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event(actor_index=1)
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data(reactor_index=1)
        tc.verify_trace_record(
            actor_index=1,
            expected_reactor_condition_results=[False, True]
        )


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["trace"])
async def test_react_trace_switched_on_actor_2(hass: HomeAssistant, workflow_name, react_component, input_boolean_component):
    """
    Test for workflow with complex trace structure where actor 1 is triggered and the test_trace is turned on:
    - No reaction entity should be created
    - 2 events should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    await react_component.async_setup(workflow_name)
    await input_boolean_component.async_turn_on("test_trace")

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_react_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event(actor_index=1)
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received(expected_count=2)
        tc.verify_reaction_event_data(event_index=0, reactor_index=0)
        tc.verify_reaction_event_data(event_index=1, reactor_index=1)
        tc.verify_trace_record(
            actor_index=1,
            expected_reactor_condition_results=[True, True]
        )

