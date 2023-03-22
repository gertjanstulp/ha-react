import pytest

from homeassistant.core import HomeAssistant

from tests.common import FIXTURE_WORKFLOW_NAME
from tests.tst_context import TstContext


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["templated"])
async def test_templated(hass: HomeAssistant, workflow_name, react_component):
    """
    Test for workflow with templates:
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    comp = await react_component
    await comp.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event(entity="actor_entity_templated", type="actor_type_templated", action="actor_action_templated")
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data(expected_entity="reactor_entity_templated", expected_type="reactor_type_templated", expected_action="reactor_action_templated")
        tc.verify_trace_record(
            expected_runtime_actor_entity="actor_entity_templated",
            expected_runtime_actor_type="actor_type_templated",
            expected_runtime_actor_action="actor_action_templated",
            expected_runtime_reactor_entity=["reactor_entity_templated"],
            expected_runtime_reactor_type=["reactor_type_templated"],
            expected_runtime_reactor_action=["reactor_action_templated"],
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["templated_state_test"])
async def test_templated_state(hass: HomeAssistant, workflow_name, template_component, react_component, input_text_component):
    """
    Test for workflow with templates containing state references
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """
    
    comp = await react_component
    await comp.async_setup(workflow_name)
    itc = await input_text_component
    await itc.async_set_value("templated_state_test", "templated_state_test")
    await template_component

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_reaction_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event(entity="actor_entity_templated_state_test", type="actor_type_templated_state_test", action="actor_action_templated_state_test")
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data(expected_entity="reactor_entity_templated_state_test", expected_type="reactor_type_templated_state_test", expected_action="reactor_action_templated_state_test")
        tc.verify_trace_record(
            expected_runtime_actor_entity="actor_entity_templated_state_test",
            expected_runtime_actor_type="actor_type_templated_state_test",
            expected_runtime_actor_action="actor_action_templated_state_test",
            expected_runtime_reactor_entity=["reactor_entity_templated_state_test"],
            expected_runtime_reactor_type=["reactor_type_templated_state_test"],
            expected_runtime_reactor_action=["reactor_action_templated_state_test"],
        )
