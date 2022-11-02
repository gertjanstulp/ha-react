import pytest

from homeassistant.core import HomeAssistant

from tests.common import FIXTURE_WORKFLOW_NAME
from tests.tst_context import TstContext


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["actor_condition"])
async def test_react_actor_condition_true(hass: HomeAssistant, workflow_name, react_component, template_component, input_boolean_component):
    """
    Test for workflow with an actor with a condition that evaluates to 'true'
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """
    
    await react_component.async_setup(workflow_name)
    await input_boolean_component.async_turn_on("test_actor_condition")

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_react_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["actor_condition"])
async def test_react_actor_condition_false(hass: HomeAssistant, workflow_name, react_component, template_component, input_boolean_component):
    """
    Test for workflow with an actor with a condition that evaluates to 'false'
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """
    
    await react_component.async_setup(workflow_name)
    await input_boolean_component.async_turn_off("test_actor_condition")

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_react_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_not_received()
        tc.verify_trace_record(expected_actor_condition_result=False)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["reactor_condition"])
async def test_react_reactor_condition_false(hass: HomeAssistant, workflow_name, react_component, input_boolean_component):
    """
    Test for workflow with a reactor with a condition that is false:
    - No reaction entity should be created
    - No event should be sent
    - Trace data should match configuration
    """

    await react_component.async_setup(workflow_name)
    await input_boolean_component.async_turn_off("test_reactor_condition")

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_react_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_not_received()
        tc.verify_trace_record(
            expected_reactor_condition_results=[False]
        )


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["reactor_condition"])
async def test_react_reactor_condition_true(hass: HomeAssistant, workflow_name, react_component, input_boolean_component):
    """
    Test for workflow with a reactor with a condition that is false:
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    await react_component.async_setup(workflow_name)
    await input_boolean_component.async_turn_on("test_reactor_condition")

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_react_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event()
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data()
        tc.verify_trace_record()
