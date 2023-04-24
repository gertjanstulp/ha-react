import pytest

from homeassistant.core import HomeAssistant

from tests.common import FIXTURE_WORKFLOW_NAME
from tests.tst_context import TstContext


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["templated"])
async def test_templated(test_context: TstContext, workflow_name: str):
    """
    Test for workflow with templates:
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    await test_context.async_start_react()
    
    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event(entity="actor_entity_templated", type="actor_type_templated", action="actor_action_templated")
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_reaction_event_data(expected_entity="reactor_entity_templated", expected_type="reactor_type_templated", expected_action="reactor_action_templated")
        test_context.verify_trace_record(
            expected_runtime_actor_entity="actor_entity_templated",
            expected_runtime_actor_type="actor_type_templated",
            expected_runtime_actor_action="actor_action_templated",
            expected_runtime_reactor_entity=["reactor_entity_templated"],
            expected_runtime_reactor_type=["reactor_type_templated"],
            expected_runtime_reactor_action=["reactor_action_templated"],
        )


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["templated_state_test"])
async def test_templated_state(test_context: TstContext, workflow_name):
    """
    Test for workflow with templates containing state references
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """
    
    await test_context.async_start_react()
    itc = await test_context.async_start_input_test()
    await itc.async_set_value("templated_state_test", "templated_state_test")
    await test_context.async_start_template()

    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event(entity="actor_entity_templated_state_test", type="actor_type_templated_state_test", action="actor_action_templated_state_test")
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_reaction_event_data(expected_entity="reactor_entity_templated_state_test", expected_type="reactor_type_templated_state_test", expected_action="reactor_action_templated_state_test")
        test_context.verify_trace_record(
            expected_runtime_actor_entity="actor_entity_templated_state_test",
            expected_runtime_actor_type="actor_type_templated_state_test",
            expected_runtime_actor_action="actor_action_templated_state_test",
            expected_runtime_reactor_entity=["reactor_entity_templated_state_test"],
            expected_runtime_reactor_type=["reactor_type_templated_state_test"],
            expected_runtime_reactor_action=["reactor_action_templated_state_test"],
        )
