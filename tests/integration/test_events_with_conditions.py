import pytest

from homeassistant.core import HomeAssistant

from tests.common import FIXTURE_WORKFLOW_NAME
from tests.tst_context import TstContext


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["actor_condition_test"])
async def test_actor_condition_true(test_context: TstContext, workflow_name: str):
    """
    Test for workflow with an actor with a condition that evaluates to 'true'
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """
    
    await test_context.async_start_react()
    ibc = await test_context.async_start_input_boolean()
    await ibc.async_turn_on("actor_condition_test")
    await test_context.async_start_template()

    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_reaction_event_data()
        test_context.verify_trace_record()


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["actor_condition_test"])
async def test_actor_condition_false(test_context: TstContext, workflow_name: str):
    """
    Test for workflow with an actor with a condition that evaluates to 'false'
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """
    
    await test_context.async_start_react()
    ibc = await test_context.async_start_input_boolean()
    await ibc.async_turn_off("actor_condition_test")
    await test_context.async_start_template()

    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_not_received()
        test_context.verify_trace_record(expected_actor_condition_result=False)


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["reactor_condition_test"])
async def test_reactor_condition_false(test_context: TstContext, workflow_name: str):
    """
    Test for workflow with a reactor with a condition that is false:
    - No reaction entity should be created
    - No event should be sent
    - Trace data should match configuration
    """

    await test_context.async_start_react()
    ibc = await test_context.async_start_input_boolean()
    await ibc.async_turn_off("reactor_condition_test")

    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_not_received()
        test_context.verify_trace_record(
            expected_reactor_condition_results=[False]
        )


@pytest.mark.parametrize(FIXTURE_WORKFLOW_NAME, ["reactor_condition_test"])
async def test_reactor_condition_true(test_context: TstContext, workflow_name: str):
    """
    Test for workflow with a reactor with a condition that is false:
    - No reaction entity should be created
    - An event should be sent
    - Event data should match configuration
    - Trace data should match configuration
    """

    await test_context.async_start_react()
    ibc = await test_context.async_start_input_boolean()
    await ibc.async_turn_on("reactor_condition_test")

    async with test_context.async_listen_reaction_event():
        test_context.verify_reaction_not_found()
        await test_context.async_send_action_event()
        test_context.verify_reaction_not_found()
        await test_context.async_verify_reaction_event_received()
        test_context.verify_reaction_event_data()
        test_context.verify_trace_record()
