import pytest

from homeassistant.core import HomeAssistant

from tests.common import FIXTURE_WORKFLOW_NAME
from tests.tst_context import TstContext


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["templated"])
async def test_react_templated(hass: HomeAssistant, workflow_name, react_component):
    """
    Test for workflow with templates:
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    await react_component.async_setup(workflow_name)

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_react_event():
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


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["templated_state"])
async def test_react_templated_state(hass: HomeAssistant, workflow_name, template_component, react_component, input_text_component):
    """
    Test for workflow with templates containing state references
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """
    
    await react_component.async_setup(workflow_name)
    await input_text_component.async_set_value("test_text", "templated_state")

    tc = TstContext(hass, workflow_name)
    async with tc.async_listen_react_event():
        tc.verify_reaction_not_found()
        await tc.async_send_action_event(entity="actor_entity_templated_state", type="actor_type_templated_state", action="actor_action_templated_state")
        tc.verify_reaction_not_found()
        await tc.async_verify_reaction_event_received()
        tc.verify_reaction_event_data(expected_entity="reactor_entity_templated_state", expected_type="reactor_type_templated_state", expected_action="reactor_action_templated_state")
        tc.verify_trace_record(
            expected_runtime_actor_entity="actor_entity_templated_state",
            expected_runtime_actor_type="actor_type_templated_state",
            expected_runtime_actor_action="actor_action_templated_state",
            expected_runtime_reactor_entity=["reactor_entity_templated_state"],
            expected_runtime_reactor_type=["reactor_type_templated_state"],
            expected_runtime_reactor_action=["reactor_action_templated_state"],
        )
